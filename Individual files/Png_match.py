import os
import re
import shutil
from datetime import datetime
from mutagen.mp4 import MP4
from PIL import Image
import piexif
import ffmpeg
import moviepy
folder_path = ''

# Create a processed folder inside the same directory
processed_folder = os.path.join(folder_path, "processed")
os.makedirs(processed_folder, exist_ok=True)

#overlay_png_on_jpeg(jpeg_path,png_path, processed_folder)


def overlay_png_on_mp4(mp4_path, png_path, processed_folder):
    """Overlay a resized PNG onto an MP4 and save in processed folder (quiet mode)."""
    if os.path.exists(png_path):
        output_path = os.path.join(processed_folder, os.path.basename(mp4_path).replace(".mp4", "_combined.mp4"))

        # Get MP4 resolution
        probe = ffmpeg.probe(mp4_path)
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
        if video_stream:
            width = video_stream["width"]
            height = video_stream["height"]

            # Use FFmpeg to scale the overlay to match the MP4 resolution
            ffmpeg.input(mp4_path).output(
                output_path,
                vf=f"[0:v]scale={width}:{height}[video]; movie={png_path},scale={width}:{height}[watermark]; [video][watermark] overlay=0:0",
            ).global_args('-loglevel', 'quiet').run(overwrite_output=True)

