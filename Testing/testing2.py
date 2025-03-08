
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

mp4_file = "/Users/samsheppard/Documents/photos/mydata~1740319422270/memories/processed/2018-06-21_966C9469-B6C6-4643-88FA-450CBE45DEDA-main_combined.mp4"


folder_path = '/Users/samsheppard/Documents/'

def overlay_png_on_mp4(mp4_path, processed_folder):
    """Overlay a resized PNG onto an MP4 and save in processed folder (quiet mode)."""
    output_path = os.path.join(processed_folder, os.path.basename(mp4_path).replace("-main_combined.mp4", "_combined.mp4"))

    try:
        # Get MP4 resolution
        probe = ffmpeg.probe(mp4_path)
        video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)

        if not video_stream:
            print(f"Error: No video stream found in {mp4_path}")
            return

        mp4_width = int(video_stream["width"])
        mp4_height = int(video_stream["height"])
        print(f"MP4 Dimensions: {mp4_width}x{mp4_height}")


        try:
            (
                ffmpeg
                .input(mp4_path)
                .output(
                    output_path,
                    vf=f"scale={mp4_height}:{mp4_width}",
                    vcodec="libx264",
                    acodec="copy",
                    format="mp4"
                )
                .global_args("-loglevel", "error")  # Suppress FFmpeg logs
                .run(overwrite_output=True)
            )
            print(f"Successfully processed: {output_path}")

        except ffmpeg.Error as e:
            print(f"FFmpeg processing error on {mp4_path}: {e}")
            return

    except ffmpeg.Error as e:
        print(f"FFmpeg error when probing {mp4_path}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

overlay_png_on_mp4(mp4_file, folder_path)
