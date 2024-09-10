import csv
import time
import random
from datetime import datetime

# Function to generate random float between -5 and 5, with 3 decimal points
def generate_random_float(minimum=-5, maximum=5, precision=3):
    return round(random.uniform(minimum, maximum), precision)

# Function to get current timestamp
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

print("Starting...")

# File to write data
filename = 'fake_data.csv'

# Headers for the CSV file
headers = [
    'idx', 'timestamp', 'Quat_W', 'Quat_X', 'Quat_Y', 'Quat_Z'
]

# Open the file in write mode
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write headers
    start_time = time.time()

    index = 0
    while True:
        # Generate row data
        row = [
            index,
            time.time() - start_time, # timestamp
            generate_random_float() + 12000, # quat_w
            generate_random_float(), # quat_x
            generate_random_float(), # quat_y
            generate_random_float()  # quat_z
        ]

        # Write row to CSV file
        writer.writerow(row)
        index += 1
        print(f"{row[0]}: {row[1::]}")

        # Sleep to maintain 100 Hz frequency
        time.sleep(0.01)
