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

folder_path = '/Users/samsheppard/Documents/'

# Create a processed folder inside the same directory
processed_folder = os.path.join(folder_path, "processed")
output_folder = os.path.join(folder_path, "output")
os.makedirs(processed_folder, exist_ok=True)


def overlay_png_on_mp4(mp4_path, png_path, processed_folder):
    """Overlay a resized PNG onto an MP4 and save in processed folder (quiet mode)."""
    if os.path.exists(png_path):
        processing_path = os.path.join(processed_folder, os.path.basename(mp4_path).replace("-main.mp4", "_combined.mp4"))

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


mp4_path = '/Users/samsheppard/Documents/2018-06-21_966C9469-B6C6-4643-88FA-450CBE45DEDA-main.mp4'
png_path = '/Users/samsheppard/Documents/2018-06-21_966C9469-B6C6-4643-88FA-450CBE45DEDA-overlay.png'

overlay_png_on_mp4(mp4_path, png_path, processed_folder) 

mp4_path = '/Users/samsheppard/Documents/2023-06-03_D8C9A173-D177-4C1B-8D1C-C0B1E0680EB3-main.mp4'
png_path = '/Users/samsheppard/Documents/2023-06-03_D8C9A173-D177-4C1B-8D1C-C0B1E0680EB3-overlay.png'

overlay_png_on_mp4(mp4_path, png_path, processed_folder) 

def overlay_png_on_jpeg(jpeg_path, png_path, processed_folder):
    """Overlay PNG on JPEG and save in processed folder."""
    output_path = os.path.join(processed_folder, os.path.basename(jpeg_path).replace("-main.jpg", "_combined.jpg"))
    
    if os.path.exists(png_path):
        image = Image.open(jpeg_path).convert("RGBA")
        overlay = Image.open(png_path).convert("RGBA").resize(image.size, Image.LANCZOS)
        # Blend images
        combined = Image.alpha_composite(image, overlay)
        Image.alpha_composite(image, overlay).convert("RGB").save(output_path, "JPEG")
    else:
        print(f'no associated png file for {jpeg_path}')
        shutil.copy(jpeg_path, output_path) 

jpeg_file = "/Users/samsheppard/Documents/photos/mydata~1740319422270/memories/test/2024-10-23_2C4A687F-4679-404E-B110-EAEC6E47127C-main.jpg"
png_file = "/Users/samsheppard/Documents/photos/mydata~1740319422270/memories/test/2024-10-23_2C4A687F-4679-404E-B110-EAEC6E47127C-overlay.png"

overlay_png_on_jpeg(jpeg_file, png_file, processed_folder)
