from bs4 import BeautifulSoup
import os
import shutil
from PIL import Image
import datetime
import cv2
from tqdm import tqdm
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

# Path to the HTML file
html_file = ".memories/memories.html"

# Use the same directory as the HTML file for media files
media_dir = os.path.dirname(html_file)

# Output directory for processed files
output_dir = "./processed_media"
os.makedirs(output_dir, exist_ok=True)

def normalize_path(path):
    """Normalize media paths relative to the HTML file."""
    path = path.replace('.//', '')  # Remove leading './' or './/'
    return os.path.normpath(os.path.join(media_dir, path))

def apply_overlay(base_img_path, overlay_img_path, output_path):
    """Apply an overlay image on top of a base image."""
    try:
        base = Image.open(base_img_path).convert("RGBA")
        overlay = Image.open(overlay_img_path).convert("RGBA")
        
        # Resize overlay to match base dimensions
        overlay = overlay.resize(base.size, Image.LANCZOS)
        
        # Composite the images
        combined = Image.alpha_composite(base, overlay)
        
        # Save the combined image
        combined.convert("RGB").save(output_path)

    except Exception as e:
        print(f"❌ Error processing image overlay: {base_img_path} with {overlay_img_path}")
        print(f"   → {e}")

def process_video_with_overlay(video_path, overlay_path, output_path):
    """Apply an overlay image on a video and save the result only."""
    try:
        video = VideoFileClip(video_path)
        overlay = ImageClip(overlay_path, ismask=False)
        
        # Resize overlay to match video size
        overlay = overlay.set_duration(video.duration).resize(height=video.h, width=video.w)

        # Combine overlay with video
        final = CompositeVideoClip([video, overlay.set_position("center")])

        # Write the combined video to output
        final.write_videofile(output_path, codec='libx264', fps=video.fps)
    except Exception as e:
        print(f"❌ Error processing video: {video_path}")
        print(f"   → {e}")

def extract_metadata_and_save(media_path, date, overlay_path=None):
    """Save image/video with metadata and apply overlay if present."""
    try:
        media_path = normalize_path(media_path)
        overlay_path = normalize_path(overlay_path) if overlay_path else None

        if not os.path.exists(media_path):
            print(f"⚠️ Missing file: {media_path}")
            return

        file_ext = os.path.splitext(media_path)[1].lower()
        output_name = f"{date}_{os.path.basename(media_path)}"
        output_path = os.path.join(output_dir, output_name)

        if file_ext in ['.jpg', '.jpeg', '.png']:
            if overlay_path and os.path.exists(overlay_path):
                apply_overlay(media_path, overlay_path, output_path)
            else:
                shutil.copy(media_path, output_path)

            # Set metadata date
            timestamp = datetime.datetime.strptime(date, "%Y-%m-%d").timestamp()
            os.utime(output_path, (timestamp, timestamp))

        elif file_ext == '.mp4':
            if overlay_path and os.path.exists(overlay_path):
                # Only save the overlayed version
                process_video_with_overlay(media_path, overlay_path, output_path)
            else:
                shutil.copy(media_path, output_path)

            # Set metadata date
            timestamp = datetime.datetime.strptime(date, "%Y-%m-%d").timestamp()
            os.utime(output_path, (timestamp, timestamp))

    except Exception as e:
        print(f"❌ Error processing file: {media_path}")
        print(f"   → {e}")

def main():
    """Main script execution."""
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    containers = soup.find_all(class_="image-container")

    # Display the progress bar
    with tqdm(total=len(containers), desc="Processing Media", unit="file") as pbar:
        for container in containers:
            try:
                img = container.find("img")
                video = container.find("video")
                date_element = container.find(class_="text-line")
                date = date_element.text if date_element else "unknown_date"

                overlay = container.find("img", class_="overlay-image")
                overlay_path = overlay['src'] if overlay else None

                media_path = img['src'] if img else video['src'] if video else None

                if media_path:
                    extract_metadata_and_save(media_path, date, overlay_path)

            except Exception as e:
                print(f"❌ Unexpected error in container: {container}")
                print(f"   → {e}")
            
            pbar.update(1)  # Increment the progress bar

    print("✅ Export completed!")

if __name__ == "__main__":
    main()
