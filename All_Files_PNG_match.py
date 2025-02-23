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

def mp4_update_metadata(file_path):
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

def jpeg_update_metadata(file_name):
    # Extracting data using regular expressions
    pattern = r'(\d{4})-(\d{2})-(\d{2})'  # Assuming the date is in the format YYYY-MM-DD
    match = re.search(pattern, file_name)

    if match:
        year, month, day = match.groups()
        print(f"Year: {year}, Month: {month}, Day: {day}")
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

def overlay_png_on_jpeg(jpeg_path, png_path):
    """Overlay a PNG on top of a JPEG and save the result."""
    if os.path.exists(png_path):
        image = Image.open(jpeg_path).convert("RGBA")  # Open JPEG as RGBA
        overlay = Image.open(png_path).convert("RGBA")  # Open PNG with transparency

        # Resize overlay using LANCZOS (high-quality resampling)
        overlay = overlay.resize(image.size, Image.ANTIALIAS)

        # Blend images
        combined = Image.alpha_composite(image, overlay)

        # Convert back to RGB and save
        output_path = jpeg_path.replace(".jpg", "_overlay.jpg").replace(".jpeg", "_overlay.jpeg")
        combined.convert("RGB").save(output_path, "JPEG")
        print(f"Overlay added to JPEG: {output_path}")

def overlay_png_on_mp4(mp4_path, png_path):
    """Overlay a PNG onto an MP4 using FFmpeg."""
    if os.path.exists(png_path):
        output_path = mp4_path.replace(".mp4", "_combined.mp4")
        
        # Use FFmpeg to overlay the PNG onto the MP4 without specifying audio_codec
        ffmpeg.input(mp4_path).output(output_path, vf=f"movie={png_path} [watermark]; [in][watermark] overlay=0:0 [out]").run(overwrite_output=True)
            
        print(f"Overlay added to MP4: {output_path}")

def move_to_processed(file_path, processed_folder):
    """Move the processed file to the 'processed' folder."""
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)  # Create folder if it doesn't exist

    new_location = os.path.join(processed_folder, os.path.basename(file_path))
    shutil.move(file_path, new_location)
    print(f"Moved to 'processed' folder: {new_location}")

def select_folder():
    """Prompt user to select a folder."""
    root = tk.Tk()
    root.withdraw()  # Don't need a full GUI, so hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing Media Files")
    return folder_path

# Select folder via file dialog
folder_path = select_folder()
if not folder_path:
    print("No folder selected. Exiting...")
    exit()

processed_folder = os.path.join(folder_path, "processed")

# Get list of files to process
all_files = [f for f in os.listdir(folder_path) if f.lower().endswith((".mp4", ".jpg", ".jpeg"))]
total_files = len(all_files)

print(f"Total files to process: {total_files}\n")

# Counters
count = 0
processed_mp4 = 0
processed_jpeg = 0

# Loop through files in the folder
for file_name in all_files:
    full_path = os.path.join(folder_path, file_name)
    count += 1
    print(f"\nProcessing file {count}/{total_files}: {file_name}")

    # Find corresponding PNG overlay
    png_path = full_path.replace("-main.mp4", "-overlay.png")

    # Process accordingly
    if file_name.lower().endswith(".mp4"):
        mp4_update_metadata(full_path)
        if os.path.exists(png_path):  # Check if PNG file exists
            overlay_png_on_mp4(full_path, png_path)
        processed_mp4 += 1
        move_to_processed(full_path, processed_folder)

    elif file_name.lower().endswith((".jpg", ".jpeg")):
        jpeg_update_metadata(full_path)
        if os.path.exists(png_path):  # Check if PNG file exists
            overlay_png_on_jpeg(full_path, png_path)
        processed_jpeg += 1
        move_to_processed(full_path, processed_folder)

# Print final summary
print("\nProcessing complete!")
print(f"Total MP4 files processed: {processed_mp4}")
print(f"Total JPEG files processed: {processed_jpeg}")
print(f"Total files processed: {processed_mp4 + processed_jpeg}")
