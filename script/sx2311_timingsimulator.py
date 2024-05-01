import os
import argparse
from ctypes import c_int32
from collections import deque

# vector data memory operations
VEC_LOAD_OPS = {"LV", "LVWS", "LVI"}
VEC_STORE_OPS = {"SV", "SVWS", "SVI"}
VEC_DATA_OPS = VEC_LOAD_OPS | VEC_STORE_OPS
# vector compute operations
VEC_BASIC_OPS = {"ADDVS", "SUBVS", "MULVS", "DIVVS", "ADDVV", "SUBVV", "MULVV", "DIVVV"}
VEC_MASK_OPS = {"SEQVV", "SNEVV", "SGTVV", "SLTVV", "SGEVV", "SLEVV", "SEQVS", "SNEVS", "SGTVS", "SLTVS", "SGEVS", "SLEVS"}
VEC_SHUFFLE_OPS = {"UNPACKLO", "UNPACKHI", "PCAKLO", "PACKHI"}
VEC_COMPUTE_OPS = VEC_BASIC_OPS | VEC_MASK_OPS | VEC_SHUFFLE_OPS
# scalar operations
VMR_SCALAR_OPS = {"CVM", "POP"}
VLR_SCALAR_OPS = {"MTCL", "MFCL"}
SCALAR_BASIC_OPS = {"LS", "SS", "ADD", "SUB", "AND", "OR", "XOR", "SLL", "SRL", "SRA"}
SCALAR_OPS = VMR_SCALAR_OPS | VLR_SCALAR_OPS | SCALAR_BASIC_OPS
# BRANCH_OPS = {"BGT", "BGE", "BLE", "BLT", "BEQ", "BNE"}
class Config(object):
    def __init__(self, iodir):
        self.filepath = os.path.abspath(os.path.join(iodir, "Config.txt"))
        self.parameters = {} # dictionary of parameter name: value as strings.

        try:
            with open(self.filepath, 'r') as conf:
                self.parameters = {line.split('=')[0].strip(): int(line.split('=')[1].split('#')[0].strip()) for line in conf.readlines() if not (line.startswith('#') or line.strip() == '')}
            print("Config - Parameters loaded from file:", self.filepath)
            print("Config parameters:", self.parameters)
        except:
            print("Config - ERROR: Couldn't open file in path:", self.filepath)
            raise
class Trace(object):
    def __init__(self, iodir):
        self.filepath = os.path.abspath(os.path.join(iodir, "trace.txt"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                for line in insf.readlines():
                    line = line.strip()
                    if line:
                        self.instructions.append(line)
            print("Trace - Instructions loaded from file:", self.filepath)
        except:
            print("Trace - ERROR: Couldn't open file in path:", self.filepath)

    def Read(self, idx): # Use this to read from IMEM.
        if idx < len(self.instructions):
            return self.instructions[idx]
        else:
            raise IndexError("Trace - ERROR: Index out of bounds.")

class Core():
    MVL = 64  # Max vector length
    def __init__(self, trace, config, pipelined=False, chaining=False):
        self.TRACE = trace
        self.CONFIG = config

        self.halted = False
        self.cycles = 0

        # Fetch
        self.PC = 0
        self.ins = None

        # Decode
        self.vrf_busyboard = [False for _ in range(8)]
        self.decode_enable = True

        # Dispatch
        self.data_queue = deque()
        self.compute_queue = deque()
        self.scalar_queue = deque()


        # Backend
        self.bank_busyboard = [0] * self.CONFIG.parameters["vdmNumBanks"]
        self.banks = None
        self.vls_ins = None
        self.vc_ins = None
        self.vls_start = False
        self.vc_start = False
        self.vls_start_up_cycles = 0
        self.vc_start_up_cycles = 0
        self.VL = 0

        # Optimization: pipelined instruction start-up
        self.pipelined = pipelined
        self.start_up = True


    def run(self):
        stop = False
        while not stop:
            self.backend()
            # frontend
            self.decode()
            self.fetch()

            self.cycles += 1

            stop = self.halted and not self.data_queue and not self.compute_queue and not self.scalar_queue and not self.vls_ins and not self.vc_ins

        print("Core - Execution completed in", self.cycles, "cycles.")
    def fetch(self):
        if self.decode_enable and not self.halted:
            self.ins = self.TRACE.Read(self.PC)
            # print("Fetched instruction:", self.ins, "in cycle:", self.cycles)
            self.ins = self.ins.split()
            self.PC += 1
            if self.ins[0] == "HALT":
                self.halted = True
            elif not self.ins[0].startswith("B"):
                self.decode_enable = False

    def check_busyboard(self, ins):

        if ins[0] not in VEC_BASIC_OPS | VEC_MASK_OPS | VEC_STORE_OPS | VEC_SHUFFLE_OPS:
            return False

        srcs = ins[-3:]
        for src in srcs:
            if src[:2] == "VR":
                src = int(src[-1])
                if self.vrf_busyboard[src]:
                    return True
        return False

    def mark_busyboard(self, ins):
        if ins[0] in VEC_BASIC_OPS | VEC_LOAD_OPS | VEC_SHUFFLE_OPS:
            des = ins[1:][0]
            des = int(des[-1])
            self.vrf_busyboard[des] = True
    def unmark_busyboard(self, ins):
        if ins[0] in VEC_BASIC_OPS | VEC_LOAD_OPS | VEC_SHUFFLE_OPS:
            des = ins[1:][0]
            des = int(des[-1])
            self.vrf_busyboard[des] = False

    def decode(self):
        if self.decode_enable:
            return

        if self.check_busyboard(self.ins):
            return

        if self.ins[0] in VEC_DATA_OPS:
            if len(self.data_queue) < self.CONFIG.parameters["dataQueueDepth"]:
                self.data_queue.append(self.ins)
                self.mark_busyboard(self.ins)
                self.decode_enable = True
        elif self.ins[0] in VEC_COMPUTE_OPS:
            if len(self.compute_queue) < self.CONFIG.parameters["computeQueueDepth"]:
                self.compute_queue.append(self.ins)
                self.mark_busyboard(self.ins)
                self.decode_enable = True
        elif self.ins[0] in SCALAR_OPS:
            self.scalar_queue.append(self.ins)
            self.decode_enable = True
        else:
            raise ValueError("Core - ERROR: Invalid instruction in decode stage:", self.ins)

    def vls_executing(self):
        if self.vls_start:
            self.vls_start = False
            addrs = self.vls_ins[-1][1:-1].split(',')
            self.banks = deque([int(addr) % self.CONFIG.parameters["vdmNumBanks"] for addr in addrs])

        if self.vls_start_up_cycles < self.CONFIG.parameters["vlsPipelineDepth"]:
            self.vls_start_up_cycles += 1
            return


        if self.banks and self.bank_busyboard[self.banks[0]] == 0:
            self.bank_busyboard[self.banks.popleft()] = self.CONFIG.parameters["vdmBankBusyTime"]

        for i in range(0, self.CONFIG.parameters["vdmNumBanks"]):
            if self.bank_busyboard[i] > 0:
                self.bank_busyboard[i] -= 1

        if not self.banks and sum(self.bank_busyboard) == 0:
            # print("Completed instruction:", self.vls_ins, "in cycle:", self.cycles)
            self.vls_start_up_cycles = 0
            self.unmark_busyboard(self.vls_ins)
            self.vls_ins = None


    def vc_executing(self):

        if self.start_up:
            # start up: vector multiply operations
            if self.vc_ins[0] in {"MULVV", "MULVS"}:
                if self.vc_start_up_cycles < self.CONFIG.parameters["pipelineDepthMul"]:
                    self.vc_start_up_cycles += 1
                    return
            # start up: vector add operations
            elif self.vc_ins[0] in {"ADDVV", "ADDVS", "SUBVV", "SUBVS"} | VEC_MASK_OPS:
                if self.vc_start_up_cycles < self.CONFIG.parameters["pipelineDepthAdd"]:
                    self.vc_start_up_cycles += 1
                    return
            # start up: vector divide operations
            elif self.vc_ins[0] in {"DIVVV", "DIVVS"}:
                if self.vc_start_up_cycles < self.CONFIG.parameters["pipelineDepthDiv"]:
                    self.vc_start_up_cycles += 1
                    return
            # start up: vector shuffle operations
            elif self.vc_ins[0] in VEC_SHUFFLE_OPS:
                if self.vc_start_up_cycles < self.CONFIG.parameters["pipelineDepthShuffle"]:
                    self.vc_start_up_cycles += 1
                    return

        # get vector length
        if self.vc_start:
            self.vc_start = False
            if self.vc_ins[0] in VEC_BASIC_OPS:
                self.VL = int(self.vc_ins[-1][1:-1])
            elif self.vc_ins[0] in VEC_MASK_OPS | VEC_SHUFFLE_OPS:
                self.VL = Core.MVL

        # vector compute
        if self.VL > 0:
            self.VL -= self.CONFIG.parameters["numLanes"]
        else:
            # print("Completed instruction:", self.vc_ins, "in cycle:", self.cycles)
            self.vc_start_up_cycles = 0
            self.unmark_busyboard(self.vc_ins)
            self.vc_ins = None

            if self.pipelined:
                if self.compute_queue:
                    self.start_up = False
                else:
                    self.start_up = True

    def backend(self):
        # scalar operations
        if self.scalar_queue:
            self.scalar_queue.popleft()

        #vector data memory operations
        if not self.vls_ins and self.data_queue:
            self.vls_ins = self.data_queue.popleft()
            self.vls_start = True
        if self.vls_ins:
            self.vls_executing()

        # vector compute operations
        if not self.vc_ins and self.compute_queue:
            self.vc_ins = self.compute_queue.popleft()
            self.vc_start = True
        if self.vc_ins:
            self.vc_executing()

    def dumptime(self, iodir):
        with open(os.path.join(iodir, "time.txt"), 'a') as timef:
            # dump config
            timef.write("# Config Parameters:\n")
            for param, val in self.CONFIG.parameters.items():
                timef.write("{}: {}\n".format(param, val))
            # dump optimization
            if self.pipelined:
                timef.write("# Optimization: Pipelined Instruction Start-up\n")
            # dump time
            timef.write("# Execution Time:\n")
            timef.write("Cycles: {}\n\n".format(self.cycles))
        print("Time Dumped to file:", os.path.join(iodir, "time.txt"))


if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Time Simulator')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    parser.add_argument("--pipelined", default=False, action='store_true', help="Pipelined instruction start-up.")
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse Config
    config = Config(iodir)
    trace = Trace(iodir)

    # Create Vector Core
    vcore = Core(trace, config, pipelined=args.pipelined)

    # Run Core
    vcore.run()   
    vcore.dumptime(iodir)

    # THE END