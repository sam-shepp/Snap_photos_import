import os
import re
from PIL import Image
from datetime import datetime
import piexif
from mutagen.mp4 import MP4
import ffmpeg
import shutil 
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

def mp4_update_metadata(file_path):
    """Extract date from filename and update MP4 metadata."""
    # Extract filename without the path
    file_name = os.path.basename(file_path)

    # Extracting date using regular expressions (YYYY-MM-DD)
    pattern = r'(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, file_name)

    if match:
        year, month, day = match.groups()
        print(f"Year: {year}, Month: {month}, Day: {day}")

        # Convert to MP4 date format (ISO 8601: YYYY-MM-DDTHH:MM:SS)
        new_date = f"{year}-{month}-{day}T00:00:00"

        # Verify file is MP4
        if not file_path.lower().endswith(".mp4"):
            print(f"Skipping non-MP4 file: {file_path}")
            return

        # Use FFmpeg to update metadata
        try:
            # FFmpeg command to set creation_time metadata
            output_path = file_path.replace(".mp4", "_dated.mp4")

            (
                ffmpeg
                .input(file_path)
                .output(
                    output_path,
                    metadata=f"creation_time={new_date}",
                    codec="copy"  # Copy streams without re-encoding
                )
                .global_args('-loglevel', 'error')  # Suppress unnecessary logs
                .run(overwrite_output=True)
            )

            print(f"Metadata updated successfully: {output_path}")

            # Replace original file with the updated one
            os.replace(output_path, file_path)

        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")

    else:
        print("No matching date pattern found in the filename.")

def jpeg_update_metadata(file_name):
    # Extracting data using regular expressions
    pattern = r'(\d{4})-(\d{2})-(\d{2})'  # Assuming the date is in the format YYYY-MM-DD
    match = re.search(pattern, file_name)

    if match:
        year, month, day = match.groups()
        #print(f"Year: {year}, Month: {month}, Day: {day}")
        exif_dict = piexif.load(file_name)
        new_date = datetime(int(year), int(month), int(day), 0, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
        #input the new Yr,month,day from the file name.
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_name)
        #print when complete
        print('Date change complete')
    else:
        print("No matching pattern found in the filename.")


def select_folder():
    """Prompt user to select a folder."""
    root = tk.Tk()
    root.withdraw()  # Don't need a full GUI, so hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Media Files")
    return folder_path

# Select folder via file dialog
folder_path = select_folder()
if not folder_path:
    #print("No folder selected. Exiting...")
    exit()

# Create a processed folder inside the same directory
processed_folder = os.path.join(folder_path, "processed")
os.makedirs(processed_folder, exist_ok=True)

# Get list of files to process
all_files = [f for f in os.listdir(folder_path) if f.lower().endswith((".mp4", ".jpg"))]
total_files = len(all_files)

#print(f"Total files to process: {total_files}\n")

# Counters
count = 0
processed_mp4 = 0
processed_jpeg = 0
skipped = 0
skipped_files = []

# Process files with a progress bar
with tqdm(total=len(all_files), desc="Processing Files", unit="file") as pbar:
    # Loop through files in the folder
    for file_name in all_files:
        full_path = os.path.join(folder_path, file_name)
        count += 1
        print(f"\nProcessing file {count}/{total_files}: {file_name}")
        pbar.update(1)

        try:
            # Process accordingly
            if file_name.lower().endswith(".mp4"):
                mp4_update_metadata(full_path)
                processed_mp4 += 1

            elif file_name.lower().endswith((".jpg")):
                jpeg_update_metadata(full_path)
                processed_jpeg += 1
        except:
            print(f'skipping: {file_name}')
            skipped_files.append(file_name)
            skipped = skipped + 1


# Print final summary
print("\nProcessing complete!")
print(f"Total MP4 files processed: {processed_mp4}")
print(f"Total JPEG files processed: {processed_jpeg}")
print(f"Total files processed: {processed_mp4 + processed_jpeg}")
print(f"Total files skipped: {skipped}")

print('skipped files:')
print(skipped_files)

print('retrying skipped files')
# Process files with a progress bar
with tqdm(total=len(skipped_files), desc="Processing Files", unit="file") as pbar:
    # Loop through files in the folder
    for file_name in skipped_files:
        full_path = os.path.join(folder_path, file_name)
        count += 1
        print(f"\nProcessing file {count}/{total_files}: {file_name}")
        pbar.update(1)

        try:
            # Process accordingly
            if file_name.lower().endswith(".mp4"):
                mp4_update_metadata(full_path)
                processed_mp4 += 1

            elif file_name.lower().endswith((".jpg")):
                jpeg_update_metadata(full_path)
                processed_jpeg += 1
        except:
            print(f'skipping: {file_name}')
            skipped_files.append(file_name)
            skipped = skipped + 1