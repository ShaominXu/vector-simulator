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

    def Read(self, idx): # Use this to read from DMEM.
        if 0 <= idx < self.size:
            return self.data[idx]
        else:
            print(self.name, "- ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)


    def Write(self, idx, val): # Use this to write into DMEM.
        if 0 <= idx < self.size:
            if val < self.min_value or val > self.max_value:
                print(self.name, "- ERROR: Value out of range at index: ", idx, " with value: ", val)
            else:
                self.data[idx] = val
        else:
            print(self.name, "- ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)

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
            if len(val) == self.vec_length:
                for va in val:
                    if va < self.min_value or va > self.max_value:
                        va = c_int32(va).value
                self.registers[idx] = val
            else:
                print(self.name, "- ERROR: Invalid vector length at index: ", idx, " with vector length: ", len(val))
        else:
            print(self.name, "- ERROR: Invalid register access at index: ", idx, " with register count: ", self.reg_count)

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
    def __init__(self, imem, sdmem, vdmem):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, 64)}
        
        self.VMR = RegisterFile("VMR", 1, 64, 1, False)
        self.VLR = RegisterFile("VLR", 1)

        self.PC = 0
        
    def execute(self, ins):
        ins = ins.strip()
        if ins.startswith("#") or ins == "":
            print("Skipping comment or empty line:", ins)
            return
        ins = ins.split("#")[0].strip()
        print("Executing instruction:", ins)
        instruction = ins.split()
        operands = []
        n = len(instruction)
        for i in range(1, n):
            if i == 1 and ((n == 4 and instruction[0] not in ["SVWS", "SVI", "SS"] and not instruction[0].startswith("B")) or instruction[0] in ["POP", "MFCL", "LV"]):
                operand = int(instruction[i][-1])
            else:
                if instruction[i].isnumeric() or instruction[i].startswith("-"):
                    operand = int(instruction[i])
                else:
                    operand = self.RFs[instruction[i][:2] + "F"].Read(int(instruction[i][-1]))
            operands.append(operand)
                
        
        if instruction[0] == "ADDVV":
            VR = [operands[1][i] + operands[2][i] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "ADDVS":
            VR = [operands[1][i] + operands[2][0] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "SUBVV":
            VR = [operands[1][i] - operands[2][i] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "SUBVS":
            VR = [operands[1][i] - operands[2][0] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "MULVV":
            VR = [operands[1][i] * operands[2][i] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "MULVS":
            VR = [operands[1][i] * operands[2][0] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "DIVVV":
            VR = [operands[1][i] // operands[2][i] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "DIVVS":
            VR = [operands[1][i] // operands[2][0] for i in range(len(operands[1]))]
            self.RFs["VRF"].Write(operands[0], VR)
        elif instruction[0] == "SEQVV":
            self.VMR.Write(0, [1 if operands[0][i] == operands[1][i] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SEQVS":
            self.VMR.Write(0, [1 if operands[0][i] == operands[1][0] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SNEVV":
            self.VMR.Write(0, [1 if operands[0][i] != operands[1][i] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SNEVS":
            self.VMR.Write(0, [1 if operands[0][i] != operands[1][0] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SLTVV":
            self.VMR.Write(0, [1 if operands[0][i] < operands[1][i] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SLTVS":
            self.VMR.Write(0, [1 if operands[0][i] < operands[1][0] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SLEVV":
            self.VMR.Write(0, [1 if operands[0][i] <= operands[1][i] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SLEVS":
            self.VMR.Write(0, [1 if operands[0][i] <= operands[1][0] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SGTVV":
            self.VMR.Write(0, [1 if operands[0][i] > operands[1][i] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SGTVS":
            self.VMR.Write(0, [1 if operands[0][i] > operands[1][0] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SGEVV":
            self.VMR.Write(0, [1 if operands[0][i] >= operands[1][i] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "SGEVS":
            self.VMR.Write(0, [1 if operands[0][i] >= operands[1][0] else 0 for i in range(len(operands[0]))])
        elif instruction[0] == "CVM":
            self.VMR.Write(0, [1 for i in range(64)])
        elif instruction[0] == "POP": #Count the number of 1s in the Vector Mask Register and store the scalar value in SR1
            self.RFs["SRF"].Write(operands[0], [sum(self.VMR.Read(0))])
        elif instruction[0] == "MTCL":
            self.VLR.Write(0, operands[0])
        elif instruction[0] == "MFCL":
            self.RFs["SRF"].Write(operands[0], self.VLR.Read(0))
        elif instruction[0] == "LV":
            VR1 = [self.VDMEM.Read(operands[1][0]+i) for i in range(64)]
            self.RFs["VRF"].Write(operands[0], VR1)
        elif instruction[0] == "SV":
            for i in range(64):
                self.VDMEM.Write(operands[1][0]+i, operands[0][i])
        elif instruction[0] == "LVWS":
            VR1 = [self.VDMEM.Read(operands[1][0]+i*operands[2][0]) for i in range(64)]
            self.RFs["VRF"].Write(operands[0], VR1)
        elif instruction[0] == "SVWS":
            for i in range(64):
                self.VDMEM.Write(operands[1][0]+i*operands[2][0], operands[0][i])
        elif instruction[0] == "LVI":
            VR1 = [self.VDMEM.Read(operands[1][0]+operands[2][i]) for i in range(64)]
            self.RFs["VRF"].Write(operands[0], VR1)
        elif instruction[0] == "SVI":
            for i in range(64):
                self.VDMEM.Write(operands[1][0]+operands[2][i], operands[0][i])
        elif instruction[0] == "LS":
            SR2 = self.SDMEM.Read(operands[1][0]+operands[2])
            self.RFs["SRF"].Write(operands[0], [SR2])
        elif instruction[0] == "SS":
            self.SDMEM.Write(operands[1][0]+operands[2], operands[0][0])
        elif instruction[0] == "ADD":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] + operands[2][0]])
        elif instruction[0] == "SUB":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] - operands[2][0]])
        elif instruction[0] == "AND":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] & operands[2][0]])
        elif instruction[0] == "OR":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] | operands[2][0]])
        elif instruction[0] == "XOR":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] ^ operands[2][0]])
        elif instruction[0] == "SLL":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] << operands[2][0]])
        elif instruction[0] == "SRL":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] >> operands[2][0]])
        elif instruction[0] == "SRA":
            self.RFs["SRF"].Write(operands[0], [operands[1][0] // (2 ** operands[2][0])])
        elif instruction[0] == "BEQ":
            if operands[0][0] == operands[1][0]:
                self.PC += operands[2] - 1
        elif instruction[0] == "BNE":
            if operands[0][0] != operands[1][0]:
                self.PC += operands[2] - 1
        elif instruction[0] == "BGT":
            if operands[0][0] > operands[1][0]:
                self.PC += operands[2] - 1
        elif instruction[0] == "BLT":
            if operands[0][0] < operands[1][0]:
                self.PC += operands[2] - 1
        elif instruction[0] == "BGE":
            if operands[0][0] >= operands[1][0]:
                self.PC += operands[2] - 1
        elif instruction[0] == "BLE":
            if operands[0][0] <= operands[1][0]:
                self.PC += operands[2] - 1
        elif instruction[0] == "UNPACKLO":
            VR2 = operands[1]
            VR3 = operands[2]
            VR1 = []
            for i in range(len(VR2)//2):
                VR1 += [VR2[i], VR3[i]]
            self.RFs["VRF"].Write(int(instruction[1][-1]), VR1)
        elif instruction[0] == "UNPACKHI":
            VR2 = operands[1]
            VR3 = operands[2]
            VR1 = []
            for i in range(len(VR2)//2):
                VR1 += [VR2[i+len(VR2)//2], VR3[i+len(VR3)//2]]
            self.RFs["VRF"].Write(int(instruction[1][-1]), VR1)
        elif instruction[0] == "PACKLO":
            VR2 = operands[1]
            VR3 = operands[2]
            VR1 = [VR2[i] for i in range(0, len(VR2), 2)] + [VR3[i] for i in range(0, len(VR3), 2)]
            self.RFs["VRF"].Write(operands[0], VR1)
        elif instruction[0] == "PACKHI":
            VR2 = operands[1]
            VR3 = operands[2]
            VR1 = [VR2[i] for i in range(1, len(VR2), 2)] + [VR3[i] for i in range(1, len(VR3), 2)]
            self.RFs["VRF"].Write(operands[0], VR1)
        elif instruction[0] == "HALT":
            print("STOP EXECUTION")
        else:
            print("ERROR: Invalid instruction:", instruction[0])
            exit(1)
        
    def run(self):
        # read instructions from IMEM and execute them
        ins = self.IMEM.Read(self.PC)
        while ins != "HALT":
            self.execute(ins)
            self.PC += 1
            if self.PC >= len(self.IMEM.instructions):
                print("ERROR: Program execution reached end of IMEM without HALT instruction.")
                break
            ins = self.IMEM.Read(self.PC)
        
        if ins == "HALT":
            self.execute(ins)
            print("Program execution completed successfully")


    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
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
    vcore = Core(imem, sdmem, vdmem)

    # Run Core
    vcore.run()   
    vcore.dumpregs(iodir)

    sdmem.dump()
    vdmem.dump()

    # THE END