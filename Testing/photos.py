import os
import re

def extract_data_from_filename(file_name):
    # Extracting data using regular expressions
    pattern = r'(\d{4})-(\d{2})-(\d{2})'  # Assuming the date is in the format YYYY-MM-DD
    match = re.search(pattern, file_name)

    if match:
        year, month, day = match.groups()
        print(f"Year: {year}, Month: {month}, Day: {day}")
    else:
        print("No matching pattern found in the filename.")

# Example usage
file_name = "/Users/samsheppard/Documents/Personal/memories/2024-01-18_DC7D2CD8-8DFC-4063-988F-375AF2732A5A-main.jpg"
extract_data_from_filename(file_name)
