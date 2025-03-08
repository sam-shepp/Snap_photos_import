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
    # Extract filename without the path
    file_name = os.path.basename(file_path)
    
    # Extracting date using regular expressions (YYYY-MM-DD)
    pattern = r'(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, file_name)

    if match:
        year, month, day = match.groups()
        #print(f"Year: {year}, Month: {month}, Day: {day}")

        # Convert to MP4 date format (YYYY-MM-DDTHH:MM:SSZ)
        new_date = f"{year}-{month}-{day}T00:00:00Z"

        # Load MP4 file metadata
        mp4_file = MP4(file_path)

        # Update the creation date metadata
        mp4_file["\xa9day"] = new_date

        # Save changes
        mp4_file.save()

        #print("Date change complete.")
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
        #print('Date change complete')
    else:
        print("No matching pattern found in the filename.")


def overlay_png_on_jpeg(jpeg_path, png_path, processed_folder):
    """Overlay PNG on JPEG and save in processed folder."""
    output_path = os.path.join(processed_folder, os.path.basename(jpeg_path).replace("-main.jpg", "_combined.jpg"))
    
    if os.path.exists(png_path):
        image = Image.open(jpeg_path).convert("RGBA")
        overlay = Image.open(png_path).convert("RGBA").resize(image.size, Image.ANTIALIAS)
        # Blend images
        combined = Image.alpha_composite(image, overlay)
        Image.alpha_composite(image, overlay).convert("RGB").save(output_path, "JPEG")
    else:
        print(f'no associated png file for {jpeg_path}')
        shutil.copy(jpeg_path, output_path) 


def overlay_png_on_mp4(mp4_path, png_path, processed_folder):
    """Overlay a resized PNG onto an MP4 and save in processed folder (quiet mode)."""
    processing_path = os.path.join(processed_folder, os.path.basename(mp4_path).replace("-main.mp4", "_combined.mp4"))

    if os.path.exists(png_path):
        print(f'processing_path: {processing_path}')

        # Get MP4 resolution
        probe = ffmpeg.probe(mp4_path)
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        if video_stream:
            width = video_stream["width"]
            height = video_stream["height"]
            print(f"MP4 Dimensions: {width}x{height}")

            if width > height:
                # Use FFmpeg to scale the overlay to match the MP4 resolution
                ffmpeg.input(mp4_path).output(
                    processing_path,
                    vf=f"[0:v]scale={height}:{width}[video]; movie={png_path},scale={height}:{width}[watermark]; [video][watermark] overlay=0:0",
                ).global_args('-loglevel', 'error').run(overwrite_output=True)

                print('finished processing file')
            else:
                # Use FFmpeg to scale the overlay to match the MP4 resolution
                ffmpeg.input(mp4_path).output(
                    processing_path,
                    vf=f"[0:v]scale={width}:{height}[video]; movie={png_path},scale={width}:{height}[watermark]; [video][watermark] overlay=0:0",
                ).global_args('-loglevel', 'error').run(overwrite_output=True)

                print('finished processing file')
    else:
        print(f'no associated png file for {mp4_path}')
        shutil.copy(mp4_path, processing_path)

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
                # Find corresponding PNG overlay
                png_path = full_path.replace("-main.mp4", "-overlay.png")
                overlay_png_on_mp4(full_path, png_path, processed_folder)
                processed_mp4 += 1

            elif file_name.lower().endswith((".jpg")):
                jpeg_update_metadata(full_path)
                # Find corresponding PNG overlay
                png_path = full_path.replace("-main.jpg", "-overlay.png")
                overlay_png_on_jpeg(full_path, png_path, processed_folder)
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
