
# Generating a vector x = {1024+512j, 1024-512j, 512+1024j, 512-1024j, . . . . (32 times)}
# real part of x = {1024, 1024, 512, 512, . . . . (32 times)} stored in address 0 ~ 127
# imaginary part of x = {512, -512, 1024, -1024, . . . . (32 times)} stored in address 128 ~ 255
vector_x = [[1024, 1024, 512, 512] * 32, [512, -512, 1024, -1024] * 32]

# Generating a vector w from 'twiddle_factors.txt'
# the Twiddle factors will have to be scaled by a factor of 1000
# real part of w stroed in address 256 ~ 319
# imaginary part of w stored in address 320 ~ 383
with open('twiddle_factors.txt', 'r') as file:
    vector_w = [line.strip().split(' = ')[1] for line in file]

w_real = []
w_imag = []
for v in vector_w:
    if v.startswith('-'):
        if '+'in v:
            w_real.append(-int(float(v.split('+')[0][1:]) * 1000))
            w_imag.append(int(float(v.split('+')[1][:-1]) * 1000))
        else:
            w_real.append(-int(float(v.split('-')[1]) * 1000))
            w_imag.append(-int(float(v.split('-')[2][:-1]) * 1000))
    else:
        if '+'in v:
            w_real.append(int(float(v.split('+')[0]) * 1000))
            w_imag.append(int(float(v.split('+')[1][:-1]) * 1000))
        else:
            w_real.append(int(float(v.split('-')[0]) * 1000))
            w_imag.append(-int(float(v.split('-')[1][:-1]) * 1000))
        print(w_real, w_imag)
vector_w = [w_real, w_imag]


# Specify the file path
output_file_path = "VDMEM.txt"

# Writing the vector to a text file
try:
    with open(output_file_path, 'w') as output_file:
        for vector in [*vector_x, *vector_w]:
            for value in vector:
                output_file.write(f"{value}\n")
    print("Vector has been successfully generated and stored in", output_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))
