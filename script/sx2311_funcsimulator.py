import os
import argparse
from ctypes import c_int32

class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Code.asm"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.strip() for ins in insf.readlines()]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.instructions[idx]
        else:
            raise ValueError("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

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

    def Read(self, idx): # Use this to read from DMEM.
        if 0 <= idx < self.size:
            return self.data[idx]
        else:
            raise ValueError(self.name + "- ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)


    def Write(self, idx, val): # Use this to write into DMEM.
        if 0 <= idx < self.size:
            if val < self.min_value or val > self.max_value:
                raise ValueError(self.name + "- ERROR: Value out of range at index: ", idx, " with value: ", val)
            else:
                self.data[idx] = val
        else:
            raise ValueError(self.name + "- ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)

class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        if self.vec_length == 1:
            # Read scalar directly, don't pass list of 1 element
            return self.registers[idx][0]
        else:
            return self.registers[idx]

    def Write(self, idx, val, mask=None, length= None):

        if length is None:
            length = self.vec_length
        if mask is None:
            mask = [1] * length

        if 0 <= idx < self.reg_count:
            if self.vec_length == 1:
                self.registers[idx][0] = c_int32(val).value
                return

            if len(val) <= self.vec_length:
                for i in range(length):
                    if mask[i]:
                        self.registers[idx][i] = c_int32(val[i]).value
            else:
                raise ValueError(self.name + "- ERROR: Invalid vector length at index: ", idx, " with vector length: ", len(val))
        else:
            raise ValueError(self.name + "- ERROR: Invalid register access at index: ", idx, " with register count: ", self.reg_count)

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

class Core():
    MVL = 64
    def __init__(self, imem, sdmem, vdmem, trace=False):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, Core.MVL)}

        self.VL = Core.MVL  # Vector Length
        self.VM = [1 for i in range(Core.MVL)]  # Vector Mask 0/1

        self.PC = 0
        self.halted = False
        # For branching
        self.branch_taken = False
        self.branch_PC = 0

        # Dynamic flow
        if trace:
            self.trace = []
        else:
            self.trace = None

    def run(self):
        # read instructions from IMEM and execute them
        while not self.halted:
            # Set to false here, if branch is taken, execution will set to True
            self.branch_taken = False

            ins = self.IMEM.Read(self.PC)
            if self.trace is not None:
                self.trace.append([ins.split("#")[0].strip(), None])
            self.execute(ins)
            # Update PC to branch target or PC+1
            if self.branch_taken:
                self.PC = self.branch_PC
            else:
                self.PC = self.PC + 1

    def trace_value(self, value):
        if self.trace is not None:
            self.trace[-1][1] = value
    def execute(self, ins):
        ins = ins.strip()
        if ins.startswith("#") or ins == "":
            print("Skipping comment or empty line:", ins)
            return
        ins = ins.split("#")[0].strip()
        print("Executing instruction:", ins)
        ins = ins.split()

        if ins[0] in ["ADDVV", "SUBVV", "MULVV", "DIVVV"]:
            self.vopvv(ins)
        elif ins[0] in ["ADDVS", "SUBVS", "MULVS", "DIVVS"]:
            self.vopvs(ins)
        elif ins[0] in ["SEQVV", "SNEVV", "SLTVV", "SLEVV", "SGTVV", "SGEVV"]:
            self.svv(ins)
        elif ins[0] in ["SEQVS", "SNEVS", "SLTVS", "SLEVS", "SGTVS", "SGEVS"]:
            self.svs(ins)
        elif ins[0] == "CVM":
            self.cvm(ins)
        elif ins[0] == "POP":
            self.pop(ins)
        elif ins[0] == "MTCL":
            self.mtcl(ins)
        elif ins[0] == "MFCL":
            self.mfcl(ins)
        elif ins[0] in ["LV", "LVWS", "LVI"]:
            self.lv(ins)
        elif ins[0] in ["SV", "SVWS", "SVI"]:
            self.sv(ins)
        elif ins[0] in ["LS"]:
            self.ls(ins)
        elif ins[0] in ["SS"]:
            self.ss(ins)
        elif ins[0] in ["ADD", "SUB", "AND", "OR", "XOR", "SLL", "SRL", "SRA"]:
            self.sopss(ins)
        elif ins[0] in ["BEQ", "BNE", "BGT", "BLT", "BGE", "BLE"]:
            self.bcond(ins)
        elif ins[0] in ["UNPACKLO", "UNPACKHI", "PACKLO", "PACKHI"]:
            self.rrs(ins)
        elif ins[0] == "HALT":
            self.halt(ins)
        else:
            print(f"Invalid instruction: {ins[0]}, line {self.PC + 1}")
            exit(1)

    def vopvv(self, ins):
        opcode, des, src1, src2 = ins
        assert des[:-1] == "VR" and src1[:-1] == "VR" and src2[:-1] == "VR"
        des = int(des[-1])
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        vec1 = self.RFs["VRF"].Read(src1)
        vec2 = self.RFs["VRF"].Read(src2)
        res = [None] * Core.MVL
        for i in range(self.VL):
            if not self.VM[i]:
                continue
            if opcode == "ADDVV":
                res[i] = vec1[i] + vec2[i]
            elif opcode == "SUBVV":
                res[i] = vec1[i] - vec2[i]
            elif opcode == "MULVV":
                res[i] = vec1[i] * vec2[i]
            elif opcode == "DIVVV":
                res[i] = int(vec1[i] / vec2[i])

        self.RFs["VRF"].Write(des, res, self.VM, self.VL)
        self.trace_value(self.VL)

    def vopvs(self, ins):
        opcode, des, src1, src2 = ins
        assert des[:-1] == "VR" and src1[:-1] == "VR" and src2[:-1] == "SR"
        des = int(des[-1])
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        vec = self.RFs["VRF"].Read(src1)
        scl = self.RFs["SRF"].Read(src2)
        res = [None] * Core.MVL
        for i in range(self.VL):
            if not self.VM[i]:
                continue
            if opcode == "ADDVS":
                res[i] = vec[i] + scl
            elif opcode == "SUBVS":
                res[i] = vec[i] - scl
            elif opcode == "MULVS":
                res[i] = vec[i] * scl
            elif opcode == "DIVVS":
                res[i] = int(vec[i] / scl)

        self.RFs["VRF"].Write(des, res, self.VM, self.VL)
        self.trace_value(self.VL)

    def svv(self, ins):
        opcode, src1, src2 = ins
        assert src1[:-1] == "VR" and src2[:-1] == "VR"
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        vec1 = self.RFs["VRF"].Read(src1)
        vec2 = self.RFs["VRF"].Read(src2)
        for i in range(Core.MVL):
            if opcode == "SEQVV":
                self.VM[i] = int(vec1[i] == vec2[i])
            elif opcode == "SNEVV":
                self.VM[i] = int(vec1[i] != vec2[i])
            elif opcode == "SLTVV":
                self.VM[i] = int(vec1[i] < vec2[i])
            elif opcode == "SLEVV":
                self.VM[i] = int(vec1[i] <= vec2[i])
            elif opcode == "SGTVV":
                self.VM[i] = int(vec1[i] > vec2[i])
            elif opcode == "SGEVV":
                self.VM[i] = int(vec1[i] >= vec2[i])

    def svs(self, ins):
        opcode, src1, src2 = ins
        assert src1[:-1] == "VR" and src2[:-1] == "SR"
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        vec = self.RFs["VRF"].Read(src1)
        scl = self.RFs["SRF"].Read(src2)
        for i in range(Core.MVL):
            if opcode == "SEQVS":
                self.VM[i] = int(vec[i] == scl)
            elif opcode == "SNEVS":
                self.VM[i] = int(vec[i] != scl)
            elif opcode == "SLTVS":
                self.VM[i] = int(vec[i] < scl)
            elif opcode == "SLEVS":
                self.VM[i] = int(vec[i] <= scl)
            elif opcode == "SGTVS":
                self.VM[i] = int(vec[i] > scl)
            elif opcode == "SGEVS":
                self.VM[i] = int(vec[i] >= scl)

    def cvm(self, ins):
        self.VM = [1 for i in range(Core.MVL)]

    def pop(self, ins):
        des = ins[1]
        assert des[:-1] == "SR"
        des = int(des[-1])
        self.RFs["SRF"].Write(des, sum(self.VM))

    def mtcl(self, ins):
        src = ins[1]
        assert src[:-1] == "SR"
        src = int(src[-1])
        self.VL = self.RFs["SRF"].Read(src)

    def mfcl(self, ins):
        des = ins[1]
        assert des[:-1] == "SR"
        des = int(des[-1])
        self.RFs["SRF"].Write(des, self.VL)

    def get_addrs(self, src1, src2=None):
        assert src1[:-1] == "SR"
        src1 = int(src1[-1])
        start_addr = self.RFs["SRF"].Read(int(src1))
        if src2 is None: # LV, SV
            addrs = list(range(start_addr, start_addr + self.VL))
        elif src2[:-1] == "SR": # LVWS, SVWS
                src2 = int(src2[-1])
                stride = self.RFs["SRF"].Read(src2)
                addrs = list(range(start_addr, start_addr + self.VL*stride, stride))
        elif src2[:-1] == "VR": # LVI, SVI
            src2 = int(src2[-1])
            offset = self.RFs["VRF"].Read(src2)
            addrs = [start_addr + offset[i] for i in range(self.VL)]
        else:
            raise ValueError(f"Invalid source: {src2}, line {self.PC}")
        return addrs

    def lv(self, ins):
        if len(ins) == 3:# LV
            opcode, des, src1 = ins
            addrs = self.get_addrs(src1)
        elif len(ins) == 4: # LVWS, LVI
            opcode, des, src1, src2 = ins
            addrs = self.get_addrs(src1, src2)
        else:
            print(f"Invalid instruction: {ins}")
        assert des[:-1] == "VR"
        des = int(des[-1])
        res = [None] * Core.MVL
        for i in range(self.VL):
            if not self.VM[i]:
                continue
            res[i] = self.VDMEM.Read(addrs[i])
        self.RFs["VRF"].Write(des, res, self.VM, self.VL)
        self.trace_value(addrs)

    def sv(self, ins):
        if len(ins) == 3: # SV
            opcode, des, src1 = ins
            addrs = self.get_addrs(src1)
        elif len(ins) == 4: # SVWS, SVI
            opcode, des, src1, src2 = ins
            addrs = self.get_addrs(src1, src2)
        else:
            print(f"Invalid instruction: {ins}")
        assert des[:-1] == "VR"
        des = int(des[-1])
        vec = self.RFs["VRF"].Read(des)
        for i in range(self.VL):
            if self.VM[i]:
                self.VDMEM.Write(addrs[i], vec[i])
        self.trace_value(addrs)

    def ls(self, ins):
        opcode, des, src, imm = ins
        assert des[:-1] == "SR" and src[:-1] == "SR"
        des = int(des[-1])
        src = int(src[-1])
        imm = int(imm)
        addr = self.RFs["SRF"].Read(src) + imm
        self.RFs["SRF"].Write(des, self.SDMEM.Read(addr))
        self.trace_value(addr)

    def ss(self, ins):
        opcode, src, des, imm = ins
        assert src[:-1] == "SR" and des[:-1] == "SR"
        src = int(src[-1])
        des = int(des[-1])
        imm = int(imm)
        addr = self.RFs["SRF"].Read(des) + imm
        self.SDMEM.Write(addr, self.RFs["SRF"].Read(src))
        self.trace_value(addr)

    def sopss(self, ins):
        opcode, des, src1, src2 = ins
        assert des[:-1] == "SR" and src1[:-1] == "SR" and src2[:-1] == "SR"
        des = int(des[-1])
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        val1 = self.RFs["SRF"].Read(src1)
        val2 = self.RFs["SRF"].Read(src2)
        res = None
        if opcode == "ADD":
            res = val1 + val2
        elif opcode == "SUB":
            res = val1 - val2
        elif opcode == "AND":
            res = val1 & val2
        elif opcode == "OR":
            res = val1 | val2
        elif opcode == "XOR":
            res = val1 ^ val2
        elif opcode == "SLL":
            res = val1 << val2
        elif opcode == "SRL":
            res = val1 >> val2
        elif opcode == "SRA":
            res = val1 // (2**val2)
        self.RFs["SRF"].Write(des, res)

    def bcond(self, ins):
        opcode, src1, src2, offset = ins
        assert src1[:-1] == "SR" and src2[:-1] == "SR"
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        offset = int(offset)
        val1 = self.RFs["SRF"].Read(src1)
        val2 = self.RFs["SRF"].Read(src2)
        taken = False
        if opcode == "BEQ":
            taken = val1 == val2
        elif opcode == "BNE":
            taken = val1 != val2
        elif opcode == "BGT":
            taken = val1 > val2
        elif opcode == "BLT":
            taken = val1 < val2
        elif opcode == "BGE":
            taken = val1 >= val2
        elif opcode == "BLE":
            taken = val1 <= val2
        self.branch_taken = taken
        self.branch_PC = self.PC + offset
        self.trace_value(self.branch_PC if taken else (self.PC + 1))

    def rrs(self, ins):
        opcode, des, src1, src2 = ins
        assert des[:-1] == "VR" and src1[:-1] == "VR" and src2[:-1] == "VR"
        des = int(des[-1])
        src1 = int(src1[-1])
        src2 = int(src2[-1])
        vec1 = self.RFs["VRF"].Read(src1)
        vec2 = self.RFs["VRF"].Read(src2)
        res = [None] * Core.MVL
        if opcode == "UNPACKLO":
            res = [vec1[i//2] if i % 2 == 0 else vec2[i//2] for i in range(Core.MVL)]
        elif opcode == "UNPACKHI":
            res = [vec1[i//2+32] if i % 2 == 0 else vec2[i//2+32] for i in range(Core.MVL)]
        elif opcode == "PACKLO":
            res = [vec1[i*2] if i < 32 else vec2[(i-32)*2] for i in range(Core.MVL)]
        elif opcode == "PACKHI":
            res = [vec1[i*2+1] if i < 32 else vec2[(i-32)*2+1] for i in range(Core.MVL)]
        self.RFs["VRF"].Write(des, res)

    def halt(self, ins):
        self.halted = True


    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

    def dumptrace(self, iodir):
        if self.trace is None:
            return

        opfilepath = os.path.abspath(os.path.join(iodir, "trace.txt"))
        try:
            with open(opfilepath, "w") as opf:
                for ins, value in self.trace:

                    if value is not None:

                        if type(value) is list:
                            value = ",".join(str(v) for v in value)

                        dins = ins.split()
                        opcode = dins[0]
                        ops = dins[1:]
                        if opcode[0] in ["L", "S"]:
                            opf.write(f"{opcode} {ops[0]} ({value})\n")
                        elif opcode[0] == "B":
                            opf.write(f"{opcode[0]} ({value})\n")
                        else:
                            opf.write(f"{ins} ({value})\n")
                    else:
                        opf.write(f"{ins}\n")
            print("Trace - Dumped trace into output file in path:", opfilepath)
        except:
            print("Trace - ERROR: Couldn't open output file in path:", opfilepath)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    parser.add_argument("--trace", default=False, action='store_true', help="Generate execution trace")
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem,  trace=args.trace)

    # Run Core
    vcore.run()   
    vcore.dumpregs(iodir)
    vcore.dumptrace(iodir)

    sdmem.dump()
    vdmem.dump()

    # THE END