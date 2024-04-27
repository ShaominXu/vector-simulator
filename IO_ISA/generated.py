import random
from ctypes import c_int32
vdmem = []
sdmem = []


vector_stride = [i for i in range(64)]
vdmem.extend(vector_stride)

# generate some necessary scalar values
scalar_zero = 0
scalar_one = 1
scalar_strip = 2
scalar_mvl = 64
scalar_cache_address = 2048
sdmem.extend([scalar_zero, scalar_one, scalar_strip, scalar_mvl, scalar_cache_address])

# random generate two vectors with length 64 and range within 32-bit signed integer
vector_a = [random.randint(-2**31, 2**31-1) for _ in range(64)]
vector_b = [random.randint(-2**31, 2**31-1) for _ in range(64)]
vdmem.extend(vector_a)
vdmem.extend(vector_b)
# random generate two integer within 32-bit signed integer
scalar_a = random.randint(-2**31, 2**31-1)
scalar_b = random.randint(-2**31, 2**31-1)
sdmem.extend([scalar_a, scalar_b])

# vector operations
vector_addvv = [a+b for a,b in zip(vector_a, vector_b)]
vector_subvv = [a-b for a,b in zip(vector_a, vector_b)]

vector_addvs = [a+scalar_a for a in vector_a]
vector_subvs = [a-scalar_a for a in vector_a]

vector_mulvv = [a*b for a,b in zip(vector_a, vector_b)]
vector_divvv = [int(a/b) for a,b in zip(vector_a, vector_b)]

vector_mulvs = [a*scalar_a for a in vector_a]
vector_divvs = [int(a/scalar_a) for a in vector_a]

vdmem.extend(vector_addvv)
vdmem.extend(vector_subvv)
vdmem.extend(vector_addvs)
vdmem.extend(vector_subvs)
vdmem.extend(vector_mulvv)
vdmem.extend(vector_divvv)
vdmem.extend(vector_mulvs)
vdmem.extend(vector_divvs)

# vector mask register operations
vector_seqvv = [int(a==b) for a,b in zip(vector_a, vector_b)]
scalar_seqvv = sum(vector_seqvv)
vector_snevv = [int(a!=b) for a,b in zip(vector_a, vector_b)]
scalar_snevv = sum(vector_snevv)
vector_sgtvv = [int(a>b) for a,b in zip(vector_a, vector_b)]
scalar_sgtvv = sum(vector_sgtvv)
vector_sltvv = [int(a<b) for a,b in zip(vector_a, vector_b)]
scalar_sltvv = sum(vector_sltvv)
vector_sgevv = [int(a>=b) for a,b in zip(vector_a, vector_b)]
scalar_sgevv = sum(vector_sgevv)
vector_slevv = [int(a<=b) for a,b in zip(vector_a, vector_b)]
scalar_slevv = sum(vector_slevv)

vector_seqvs = [int(a==scalar_a) for a in vector_a]
scalar_seqvs = sum(vector_seqvs)
vector_snevs = [int(a!=scalar_a) for a in vector_a]
scalar_snevs = sum(vector_snevs)
vector_sgtvs = [int(a>scalar_a) for a in vector_a]
scalar_sgtvs = sum(vector_sgtvs)
vector_sltvs = [int(a<scalar_a) for a in vector_a]
scalar_sltvs = sum(vector_sltvs)
vector_sgevs = [int(a>=scalar_a) for a in vector_a]
scalar_sgevs = sum(vector_sgevs)
vector_slevs = [int(a<=scalar_a) for a in vector_a]
scalar_slevs = sum(vector_slevs)

sdmem.extend([scalar_seqvv, scalar_snevv, scalar_sgtvv, scalar_sltvv, scalar_sgevv, scalar_slevv])
sdmem.extend([scalar_seqvs, scalar_snevs, scalar_sgtvs, scalar_sltvs, scalar_sgevs, scalar_slevs])
# vector length register operations

# memory access operations

# scalar operations
scalar_add = scalar_a + scalar_b
scalar_sub = scalar_a - scalar_b
scalar_and = scalar_a & scalar_b
scalar_or = scalar_a | scalar_b
scalar_xor = scalar_a ^ scalar_b
scalar_sll = scalar_a << scalar_one
scalar_srl = scalar_a >> scalar_one
scalar_sra = scalar_a // (2**scalar_one)

scalar_beq = int(scalar_a == scalar_b)
scalar_bne = int(scalar_a != scalar_b)
scalar_bgt = int(scalar_a > scalar_b)
scalar_blt = int(scalar_a < scalar_b)
scalar_bge = int(scalar_a >= scalar_b)
scalar_ble = int(scalar_a <= scalar_b)

sdmem.extend([scalar_add, scalar_sub, scalar_and, scalar_or, scalar_xor, scalar_sll, scalar_srl, scalar_sra])
sdmem.extend([scalar_beq, scalar_bne, scalar_bgt, scalar_blt, scalar_bge, scalar_ble])
# register-register shuffle operations
vector_unpacklo = [vector_a[i//2] if i % 2 == 0 else vector_b[i//2] for i in range(64)]
vector_unpackhi = [vector_a[i//2+32] if i % 2 == 0 else vector_b[i//2+32] for i in range(64)]
vector_packlo = [vector_a[i*2] if i < 32 else vector_b[(i-32)*2] for i in range(64)]
vector_packhi = [vector_a[i*2+1] if i < 32 else vector_b[(i-32)*2+1] for i in range(64)]

vdmem.extend(vector_unpacklo)
vdmem.extend(vector_unpackhi)
vdmem.extend(vector_packlo)
vdmem.extend(vector_packhi)
# Specify the file path
vdmem_file_path = "VDMEM.txt"
sdmem_file_path = "SDMEM.txt"

max_value = pow(2, 31) - 1
# Writing the vector to a text file
try:
    with open(vdmem_file_path, 'w') as output_file:
        for value in vdmem:
            value = c_int32(value).value
            output_file.write(f"{value}\n")
    print("Vector has been successfully generated and stored in", vdmem_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))

try:
    with open(sdmem_file_path, 'w') as output_file:
        for value in sdmem:
            output_file.write(f"{value}\n")
    print("Scalar has been successfully generated and stored in", sdmem_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))
