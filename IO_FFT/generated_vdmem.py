
# Generating a matrix of size 256x256: {-1, 1, -1, 1, -1, 1, -1, 1, ...} in odd rows and {1, -1, 1, -1, 1, -1, 1, -1, ...} in even rows
matrix_f = [[-1 if j % 2 == 0 else 1 for j in range(256)] if i % 2 == 0 else [1 if j % 2 == 0 else -1 for j in range(256)] for i in range(256)]


# Specify the file path
output_file_path = "VDMEM.txt"

# Writing the vector to a text file
try:
    with open(output_file_path, 'w') as output_file:
        for vector in [*matrix_f]:
            for value in vector:
                output_file.write(f"{value}\n")
    print("Vector has been successfully generated and stored in", output_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))
