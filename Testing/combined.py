import os
import re
from PIL import Image
from datetime import datetime
import piexif

#funciton that takes out the date from the pattern in the image title
def extract_data_from_filename(file_name):
    # Extracting data using regular expressions
    pattern = r'(\d{4})-(\d{2})-(\d{2})'  # Assuming the date is in the format YYYY-MM-DD
    match = re.search(pattern, file_name)

    #If statement that is able to chang the metadata of the jpg file
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
    #print when fails
    else:
        print("No matching pattern found in the filename.")

