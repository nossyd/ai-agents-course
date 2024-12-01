import json

# Path to your JSON file
file_path = '/autograder/results/results.json'

# Read the JSON data from the file
try:
    with open(file_path, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"File not found: {file_path}")
    exit(1)

# Update the value (for example, updating 'age')
data['visibility'] = 'hidden'
data['stdout_visibility'] = 'hidden'

# Write the updated JSON data back to the file
with open(file_path, 'w') as file:
    json.dump(data, file)

print("JSON file updated successfully.")
