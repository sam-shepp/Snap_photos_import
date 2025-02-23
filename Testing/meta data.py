from PIL import Image
from datetime import datetime
'''from PIl.ExifTags import TAGS'''
import piexif

jpg_file_path = "/Users/samsheppard/Documents/Personal/Testphoto.jpg"


filename = '/Users/samsheppard/Documents/Personal/Testphoto.jpg'
exif_dict = piexif.load(filename)
new_date = datetime(2018, 1, 1, 0, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
exif_bytes = piexif.dump(exif_dict)
piexif.insert(exif_bytes, filename)
'''

print(results)

def display_jpg_metadata(file_path):
    try:
        # Open the image file
        img = Image.open(file_path)

        # Check if the file has EXIF data
        if hasattr(img, '_getexif'):
            exif_data = img._getexif()

            # Check if EXIF data exists
            if exif_data is not None:
                # Extract creation date and time from EXIF data
                creation_datetime = exif_data.get(0x9003)  # Tag for DateTimeOriginal

                if creation_datetime:
                    # Convert the creation date and time to a datetime object
                    creation_datetime = datetime.strptime(creation_datetime, "%Y:%m:%d %H:%M:%S")
                    print("Creation Date and Time:", creation_datetime)
                else:
                    print("Creation date and time information not found in EXIF data.")
            else:
                print("No EXIF data found in the image.")
        else:
            print("EXIF data not available for this image.")
    except Exception as e:
        print(f"Error: {e}")


# Example usage
jpg_file_path = "/Users/samsheppard/Documents/Personal/Testphoto.jpg"
display_jpg_metadata(jpg_file_path)
'''