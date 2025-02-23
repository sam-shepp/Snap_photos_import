import os
import re
import shutil
from datetime import datetime
from mutagen.mp4 import MP4
from PIL import Image
import piexif
import ffmpeg
import moviepy

def overlay_png_on_jpeg(jpeg_path, png_path, processed_folder):
    """Overlay PNG on JPEG and save in processed folder."""
    if os.path.exists(png_path):
        image = Image.open(jpeg_path).convert("RGBA")
        overlay = Image.open(png_path).convert("RGBA").resize(image.size, Image.ANTIALIAS)
        # Blend images
        combined = Image.alpha_composite(image, overlay)
        output_path = os.path.join(processed_folder, os.path.basename(jpeg_path).replace(".jpg", "_overlay.jpg").replace(".jpeg", "_overlay.jpeg"))
        Image.alpha_composite(image, overlay).convert("RGB").save(output_path, "JPEG")

jpeg_path = '/Users/samsheppard/Documents/2024-10-23_2C4A687F-4679-404E-B110-EAEC6E47127C-main_overlay.jpg'
png_path = '/Users/samsheppard/Documents/2024-10-23_2C4A687F-4679-404E-B110-EAEC6E47127C-overlay.png'
folder_path = '/Users/samsheppard/Documents/'

# Create a processed folder inside the same directory
processed_folder = os.path.join(folder_path, "processed")
os.makedirs(processed_folder, exist_ok=True)

overlay_png_on_jpeg(jpeg_path,png_path, processed_folder)

""" 
def overlay_png_on_mp4(mp4_path, png_path):
    ""Overlay a PNG onto an MP4 using FFmpeg.""
    if os.path.exists(png_path):
        output_path = mp4_path.replace(".mp4", "_overlay.mp4")
        
        
            # Use FFmpeg to overlay the PNG onto the MP4 without specifying audio_codec
        ffmpeg.input(mp4_path).output(output_path, vf=f"movie={png_path} [watermark]; [in][watermark] overlay=0:0 [out]").run(overwrite_output=True)
            
        print(f"Overlay added to MP4: {output_path}")
    


mp4_path = '/Users/samsheppard/Documents/Personal/memories/2018-06-21_966C9469-B6C6-4643-88FA-450CBE45DEDA-main.mp4'
png_path = '/Users/samsheppard/Documents/Personal/memories/2018-06-21_966C9469-B6C6-4643-88FA-450CBE45DEDA-overlay.png'

overlay_png_on_mp4(mp4_path, png_path) """