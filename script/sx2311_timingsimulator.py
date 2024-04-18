import os
import argparse
from ctypes import c_int32
from collections import deque

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

class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Code.asm"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.split('#')[0].strip() for ins in insf.readlines() if not (ins.startswith('#') or ins.strip() == '')]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)
            raise

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.instructions[idx]
        else:
            print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
            print(self.name, "- Data loaded from file:", self.ipfilepath)
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            print(self.name, "- ERROR: Couldn't open input file in path:", self.ipfilepath)
            raise

    def Read(self, idx): # Use this to read from DMEM.
        pass # Replace this line with your code here.

    def Write(self, idx, val): # Use this to write into DMEM.
        pass # Replace this line with your code here.

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)
            raise

class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32, signed = True):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1) if signed else 0
        self.max_value  = pow(2, self.reg_bits-1) - 1 if signed else pow(2, self.reg_bits) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        return self.registers[idx]

    def Write(self, idx, val):
        if 0 <= idx < self.reg_count:
            if len(val) <= self.vec_length:
                for i, va in enumerate(val):
                    if va < self.min_value or va > self.max_value:
                        if self.reg_bits == 32:
                            va = c_int32(va).value  # Clamp the value to 32-bit signed integer range when overflow occurs.
                    self.registers[idx][i] = va
            else:
                print(self.name, "- ERROR: Invalid vector length at index: ", idx, " with vector length: ", len(val))
        else:
            print(self.name, "- ERROR: Invalid register access at index: ", idx, " with register count: ",
                  self.reg_count)

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)
            raise

class Core():
    def __init__(self, imem, sdmem, vdmem, config):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem
        self.CONFIG = config

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, 64)}

        self.VMR = RegisterFile("VMR", 1, 64, 1, False)
        self.VLR = RegisterFile("VLR", 1)

        self.VMR.Write(0, [1 for _ in range(64)])
        self.VLR.Write(0, [64])
        
        self.PC = 0
        self.halt = False
        self.cycle = 0
        self.vls_cycles = 0
        self.vls_cycles_target = 0
        self.vmul_cycles = 0
        self.vmul_cycles_target = 0
        self.vdiv_cycles = 0
        self.vdiv_cycles_target = 0
        self.vadd_cycles = 0
        self.vadd_cycles_target = 0
        self.shuffle_cycles = 0
        self.shuffle_cycles_target = 0


        self.busy_board = [False for _ in range(8)]
        self.data_queue = deque()
        self.compute_queue = deque()
        self.scalar_queue = deque()
        self.ins_queue = deque()

        self.vmul_ins = set(["MULVV", "MULVS"])
        self.vdiv_ins = set(["DIVVV", "DIVVS"])
        self.vadd_ins = set(["ADDVV", "SUBVV", "ADDVS", "SUBVS"])
        self.vmask_ins = set(["SEQVV", "SNEVV", "SLTVV", "SGTVV", "SLEVV", "SGEVV", "SEQVS", "SNEVS", "SLTVS", "SGTVS", "SLEVS", "SGEVS"])
        self.shuffle_ins = set(["UNPACKLO", "UNPACKHI", "PACKLO", "PACKHI"])
        self.vl_ins = set(["LV", "LVWS", "LVI"])
        self.vs_ins = set(["SV", "SVWS", "SVI"])
        self.brach_ins = set(["BEQ", "BNE", "BLT", "BGT", "BLE", "BGE"])

        self.vector_data_ins = self.vl_ins.union(self.vs_ins)
        self.vector_compute_ins = self.vmul_ins.union(self.vdiv_ins).union(self.vadd_ins).union(self.vmask_ins).union(self.shuffle_ins)
        self.scalar_ins = set(["CVM", "POP", "LS", "SS","ADD", "SUB", "AND", "OR", "XOR", "SLL", "SRL"]).union(self.brach_ins)


    def step(self):

        ins = self.IMEM.Read(self.PC)
        self.PC += 1

        ins = ins.strip()
        if ins.startswith("#") or ins == "":
            print("Skipping comment or empty line:", ins)
            return

        ins = ins.split("#")[0].strip()
        print("Executing instruction:", ins)
        inst = ins.split()
        self.cycle += 1

        #---------------Execute Stage--------------
        if self.data_queue:
            if self.vls_cycles == 0:
                ins = self.data_queue[0]
                if (ins[0] in ["SV", "SVWS"] and not self.busy_board[int(ins[1][-1])]) or \
                        (ins[0] in ["LVI", "SVI"] and not self.busy_board[int(ins[1][-1])] and not self.busy_board[int(ins[-1][-1])]) or \
                        ins[0] in ["LV", "LVWS"]:
                    vls_ins = self.data_queue.popleft()
                    self.vls_cycles += 1
                    if self.VLR.Read(0)[0] % self.CONFIG.parameters["vdmNumBanks"] == 0:
                        self.vls_cycles_target = self.CONFIG.parameters["vlsPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["vdmNumBanks"]
                    else:
                        self.vls_cycles_target = self.CONFIG.parameters["vlsPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["vdmNumBanks"] + 1
            elif self.vls_cycles == self.vls_cycles_target:
                self.vls_cycles = 0
            else:
                self.vls_cycles += 1

        if self.compute_queue:
            ins = self.compute_queue[0]
            if ins[0] in self.vmul_ins:
                if self.vmul_cycles == 0:
                    if not self.busy_board[int(ins[-1][-1])] and not self.busy_board[int(ins[-2][-1])]:
                        self.compute_queue.popleft()
                        self.vmul_cycles += 1
                        if self.VLR.Read(0)[0] % self.CONFIG.parameters["numLanes"] == 0:
                            self.vmul_cycles_target = self.CONFIG.parameters["vmulPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"]
                        else:
                            self.vmul_cycles_target = self.CONFIG.parameters["vmulPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"] + 1
                else:
                    self.vmul_cycles += 1
            elif ins[0] in self.vdiv_ins:
                if self.vdiv_cycles == 0:
                    if not self.busy_board[int(ins[-1][-1])] and not self.busy_board[int(ins[-2][-1])]:
                        self.compute_queue.popleft()
                        self.vdiv_cycles += 1
                        if self.VLR.Read(0)[0] % self.CONFIG.parameters["numLanes"] == 0:
                            self.vdiv_cycles_target = self.CONFIG.parameters["vdivPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"]
                        else:
                            self.vdiv_cycles_target = self.CONFIG.parameters["vdivPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"] + 1
                elif self.vdiv_cycles == self.vdiv_cycles_target:
                    self.vdiv_cycles = 0
                    # set busy board to false
                else:
                    self.vdiv_cycles += 1
            elif ins[0] in self.vadd_ins:
                if self.vadd_cycles == 0:
                    if not self.busy_board[int(ins[-1][-1])] and not self.busy_board[int(ins[-2][-1])]:
                        self.compute_queue.popleft()
                        self.vadd_cycles += 1
                        if self.VLR.Read(0)[0] % self.CONFIG.parameters["numLanes"] == 0:
                            self.vadd_cycles_target = self.CONFIG.parameters["vaddPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"]
                        else:
                            self.vadd_cycles_target = self.CONFIG.parameters["vaddPipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"] + 1
                elif self.vadd_cycles == self.vadd_cycles_target:
                    self.vadd_cycles = 0
                    # set busy board to false
                else:
                    self.vadd_cycles += 1
            elif ins[0] in self.shuffle_ins:
                if self.shuffle_cycles == 0:
                    if not self.busy_board[int(ins[-1][-1])] and not self.busy_board[int(ins[-2][-1])]:
                        self.compute_queue.popleft()
                        self.shuffle_cycles += 1
                        if self.VLR.Read(0)[0] % self.CONFIG.parameters["numLanes"] == 0:
                            self.shuffle_cycles_target = self.CONFIG.parameters["shufflePipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"]
                        else:
                            self.shuffle_cycles_target = self.CONFIG.parameters["shufflePipelineDepth"] + self.VLR.Read(0)[0] // self.CONFIG.parameters["numLanes"] + 1
                elif self.shuffle_cycles == self.shuffle_cycles_target:
                    self.shuffle_cycles = 0
                    # set busy board to false
                else:
                    self.shuffle_cycles += 1


        if self.scalar_queue:
            self.scalar_queue.popleft()

        # set busy board to false


        #---------------Decode Stage---------------
        if self.ins_queue:
            self.decode(self.ins_queue.popleft())


        #---------------Fetch Stage----------------
        #Q: how to deal with HALT instruction?
        if inst[0] in self.brach_ins:
            self.PC += int(inst[3]) - 1
        else:
            self.ins_queue.append(inst)

    def decode(self, ins):
        if ins[0] in self.vector_data_ins:
            if len(self.data_queue) < int(self.CONFIG.parameters["dataQueueDepth"]):
                self.data_queue.append(ins)
                if ins[0] in self.vl_ins:
                    self.busy_board[int(ins[1][-1])] = True
            else:
                self.PC -= 1

        elif ins[0] in self.vector_compute_ins:
            if len(self.compute_queue) < int(self.CONFIG.parameters["computeQueueDepth"]):
                self.compute_queue.append(ins)
                if ins[0] in self.vmul_ins.union(self.vdiv_ins).union(self.vadd_ins).union(self.shuffle_ins):
                    self.busy_board[int(ins[1][-1])] = True
            else:
                self.PC -= 1

        elif ins[0] in self.scalar_ins:
            self.scalar_queue.append(ins)

    def run(self):
        while(True):
            if self.halt:
                break
            self.step()

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Functional Simulator')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse Config
    config = Config(iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem, config)

    # Run Core
    vcore.run()   
    #vcore.dumpregs(iodir)

    #sdmem.dump()
    #vdmem.dump()

    # THE END