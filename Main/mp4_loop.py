import os
import re
from datetime import datetime
from mutagen.mp4 import MP4

count = 0

def extract_date_from_filename(file_path):
    # Extract filename without the path
    file_name = os.path.basename(file_path)
    
    # Extracting date using regular expressions (YYYY-MM-DD)
    pattern = r'(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, file_name)

    if match:
        year, month, day = match.groups()
        print(f"Year: {year}, Month: {month}, Day: {day}")

        # Convert to MP4 date format (YYYY-MM-DDTHH:MM:SSZ)
        new_date = f"{year}-{month}-{day}T00:00:00Z"

        # Load MP4 file metadata
        mp4_file = MP4(file_path)

        # Update the creation date metadata
        mp4_file["\xa9day"] = new_date

        # Save changes
        mp4_file.save()

        print("Date change complete.")
    else:
        print("No matching date pattern found in the filename.")

# Example file path
folder_path = "/Users/samsheppard/Documents/Personal/memories"


for file_name in os.listdir(folder_path):
    if file_name.lower().endswith(".mp4"):  # Filter only MP4 files
        full_path = os.path.join(folder_path, file_name)
        count += 1
        print(count)
        print(file_name)
        print(full_path)
        extract_date_from_filename(full_path)  # Pass full file path


