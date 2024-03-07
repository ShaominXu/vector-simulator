# Generating a vector {0, 1, 2, 3, ..., 449}
vector_data = list(range(450))

# Specify the file path
output_file_path = "VDMEM.txt"

# Writing the vector to a text file
try:
    with open(output_file_path, 'w') as output_file:
        for value in vector_data:
            output_file.write(f"{value}\n")
    print("Vector has been successfully generated and stored in", output_file_path)
except Exception as e:
    print("Error occurred while writing to the file:", str(e))
