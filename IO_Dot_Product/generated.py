# Generating a vector {0, 1, 2, 3, ..., 449}
vector_a = list(range(450))
vector_b = list(range(450))

# Specify the file path
vdmem_file_path = "VDMEM.txt"

# Writing the vector to a text file
try:
    with open(vdmem_file_path, 'w') as output_file:
        for value in [*vector_a, *vector_b]:
            output_file.write(f"{value}\n")
    print("Vector has been successfully generated and stored in", vdmem_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))

# calculate the dot product to compare with the expected output
expected_output = sum([a*b for a,b in zip(vector_a, vector_b)])
print("Expected output:", expected_output)
# some necessary scalar values
scalar_VML = 64
scalar_input_vector_length = 450
scalar_output_save_address = 2048
scalar_res = scalar_input_vector_length % scalar_VML
scalar_one = 1

sdmem = []

sdmem.append(scalar_VML)
sdmem.append(scalar_input_vector_length)
sdmem.append(scalar_output_save_address)
sdmem.append(scalar_res)
sdmem.append(scalar_one)
sdmem.append(expected_output)

sdmem_file_path = "SDMEM.txt"
try:
    with open(sdmem_file_path, 'w') as output_file:
        for value in sdmem:
            output_file.write(f"{value}\n")
    print("Scalar data has been successfully generated and stored in", sdmem_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))