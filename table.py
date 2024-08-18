from tabulate import tabulate

# Function to convert status codes to symbols
def get_status_symbol(file_exists, file_size_verified):
    exists_symbol = "✅" if file_exists == 1 else "❌"
    size_verified_symbol = "✅" if file_size_verified == 1 else "❌" if file_size_verified == 0 else "—"
    return exists_symbol, size_verified_symbol

# Function to generate the table
def generate_file_status_table(file_status_list):
    table = []

    # Adding header row
    table.append(["S.No.", "Filename", "File Path", "File Exists", "File Size Verified"])

    # Adding file status rows
    for i, (filename, file_path, file_exists, file_size_verified) in enumerate(file_status_list, start=1):
        exists_symbol, size_verified_symbol = get_status_symbol(file_exists, file_size_verified)
        table.append([i, filename, file_path, exists_symbol, size_verified_symbol])

    # Print the table
    print(tabulate(table, headers="firstrow", tablefmt="grid"))

# Example usage
file_status_list = [
    ("file1.txt", "/path/to/file1.txt", 1, 1),
    ("file2.txt", "/path/to/file2.txt", 0, 0),
    ("file3.txt", "/path/to/file3.txt", 1, 2),
    ("file4.txt", "/path/to/file4.txt", 0, 1)
]

generate_file_status_table(file_status_list)
