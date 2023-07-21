import csv
import subprocess

def execute_addition(numbers):
    command = ["python", "./automation_test/add_numbers.py"] + numbers
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()

if __name__ == "__main__":
    csv_file = "./automation_test/input_numbers.csv"  # Replace with the actual name of your CSV file
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            numbers = [n for n in row if n.strip()]  # Extract non-empty numbers from each row
            result = execute_addition(numbers)
            print("Numbers:", numbers, "| Result:", result)
