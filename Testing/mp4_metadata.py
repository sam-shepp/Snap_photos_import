import os
import re
import ffmpeg
from mutagen.mp4 import MP4

import os
import re
import ffmpeg
from mutagen.mp4 import MP4

def extract_date_from_filename(file_path):
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
        #new_date = f"2025-03-20T00:00:00"

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



# Example file path
file_path = "/Users/samsheppard/Documents/photos/mydata~1740319422270/memories/processed/2018-07-17_4BB9636E-A96E-4762-9E6A-DC42A8F8ACF7_combined.mp4"

# Run function
extract_date_from_filename(file_path)
