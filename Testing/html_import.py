from bs4 import BeautifulSoup
import os
import shutil
from PIL import Image
import datetime
from tqdm import tqdm
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

# Path to the original HTML file
html_file = "/Users/samsheppard/Documents/photos/mydata~1740319422270/memories/memories.html"

# Use the same directory as the HTML file for media files
media_dir = os.path.dirname(html_file)

# Output directory for processed media files
output_dir = "/Users/samsheppard/Documents/photos/processed_media"
os.makedirs(output_dir, exist_ok=True)

# Output HTML file with the new references
output_html = os.path.join(output_dir, "processed_memories.html")

def normalize_path(path):
    """Normalize media paths relative to the HTML file."""
    if not path:
        return None
    path = path.replace('.//', '')  # Clean up './' and './/'
    normalized_path = os.path.normpath(os.path.join(media_dir, path))

    if not os.path.exists(normalized_path):
        print(f"⚠️ File not found: {normalized_path}")
        return None

    return normalized_path

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
    """Apply an overlay image on a video and save the result."""
    try:
        video = VideoFileClip(video_path)
        overlay = ImageClip(overlay_path, ismask=False)

        # Resize the overlay to match video dimensions
        overlay = overlay.resize(height=video.h, width=video.w)
        overlay = overlay.set_duration(video.duration)

        # Combine overlay with video
        final = CompositeVideoClip([video, overlay.set_position("center")])

        # Save the combined video
        final.write_videofile(output_path, codec='libx264', fps=video.fps)

        print(f"✅ Combined video saved: {output_path}")

    except Exception as e:
        print(f"❌ Error processing video: {video_path} with overlay: {overlay_path}")
        print(f"   → {e}")

def extract_metadata_and_save(media_path, date, overlay_path=None):
    """Save image/video with metadata and apply overlay if present."""
    try:
        # Normalize paths
        media_path = normalize_path(media_path)
        overlay_path = normalize_path(overlay_path) if overlay_path else None

        if not media_path or not os.path.exists(media_path):
            print(f"⚠️ Missing media file: {media_path}")
            return None

        file_ext = os.path.splitext(media_path)[1].lower()
        output_name = f"{date}_{os.path.basename(media_path)}"
        output_path = os.path.join(output_dir, output_name)

        # ✅ Image Processing
        if file_ext in ['.jpg', '.jpeg', '.png']:
            if overlay_path and os.path.exists(overlay_path):
                apply_overlay(media_path, overlay_path, output_path)
            else:
                shutil.copy(media_path, output_path)

            # Set metadata date
            timestamp = datetime.datetime.strptime(date, "%Y-%m-%d").timestamp()
            os.utime(output_path, (timestamp, timestamp))

        # ✅ Video Processing
        elif file_ext == '.mp4':
            if overlay_path and os.path.exists(overlay_path):
                combined_output_path = os.path.join(output_dir, f"combined_{os.path.basename(media_path)}")
                process_video_with_overlay(media_path, overlay_path, combined_output_path)
                return combined_output_path
            else:
                shutil.copy(media_path, output_path)

            # Set metadata date
            timestamp = datetime.datetime.strptime(date, "%Y-%m-%d").timestamp()
            os.utime(output_path, (timestamp, timestamp))

        return output_path

    except Exception as e:
        print(f"❌ Error processing file: {media_path}")
        print(f"   → {e}")
        return None

def main():
    """Main script execution."""
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract metadata and style
    head = soup.head

    # ✅ Handle missing head by adding a default one
    if head is None:
        print("⚠️ No <head> section found. Adding default head.")
        head = BeautifulSoup("""
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Memories</title>
            <style>
                .image-container {
                    position: relative;
                    display: inline-block;
                    margin: 10px;
                }
                .overlay-image {
                    position: absolute;
                    top: 0;
                    left: 0;
                    max-width: 100%;
                    max-height: 100%;
                }
                .text-line {
                    display: block;
                    margin-top: 5px;
                }
            </style>
        </head>
        """, "html.parser").head

    containers = soup.find_all(class_="image-container")

    # Create new HTML document
    new_soup = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")
    new_soup.head.replace_with(head)

    # Display the progress bar
    with tqdm(total=len(containers), desc="Processing Media", unit="file") as pbar:
        for container in containers:
            try:
                # Extract date
                date_element = container.find(class_="text-line")
                date = date_element.text.strip() if date_element else "unknown_date"

                # Handle both images and nested videos
                img = container.find("img", class_=None)
                video = container.find("video")
                overlay = container.find("img", class_="overlay-image")

                media_path = None
                overlay_path = None

                if video:
                    # Handle nested video with overlay
                    media_path = video['src']
                    if overlay:
                        overlay_path = overlay['src']
                elif img:
                    # Handle standalone image with optional overlay
                    media_path = img['src']
                    if overlay:
                        overlay_path = overlay['src']

                # Process the media and get the new file path
                if media_path:
                    new_media_path = extract_metadata_and_save(media_path, date, overlay_path)

                    # Update the HTML reference
                    if new_media_path:
                        new_rel_path = os.path.relpath(new_media_path, output_dir)
                        new_container = container

                        # Update image or video references
                        if video:
                            new_container.video['src'] = new_rel_path
                        elif img:
                            new_container.img['src'] = new_rel_path

                        new_soup.body.append(new_container)

            except Exception as e:
                print(f"❌ Unexpected error in container: {container}")
                print(f"   → {e}")

            pbar.update(1)

    # Save the new HTML file
    with open(output_html, "w", encoding="utf-8") as out_file:
        out_file.write(new_soup.prettify())

    print(f"✅ Export completed! New HTML saved at: {output_html}")

if __name__ == "__main__":
    main()
