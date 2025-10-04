**Snapchat Photo Importer and Metadata Updater**
=============================

# Introduction
The purpose of this tool is to extract photos and videos from Snapchat Memories storage and import them into your iPhone's Camera Roll, preserving metadata.

## Background
When exporting media from Snapchat using their UI, users are limited to 20 photos at a time with no metadata exported. However, it's possible to export all media through the Snapchat settings, resulting in separate zip files without associated metadata for MP4 and JPEG files.

### Process

#### Exporting Media from Snapchat

1. Use the Snapchat app to export your media content.
2. After submitting the request, wait for an email with a link to download your content as zip files.
3. These zip files will contain individual media files and an overlay file (if applicable).

#### Importing Media into Camera Roll

1. Unzip the downloaded zip files containing 10GB of media.
2. Run the `main.py` file, selecting the folder where the content is stored.
3. A new "processed" folder will be created within the structure, containing all final processed files.

*Best Practices (on a MacBook)*
-------------------------

* Select all output files and drag them into the Apple Photos app to store your media content.

# Note

This project was initially developed as a personal endeavor due to recent Snapchat news about removing free storage for users. We're now making it publicly available. Contributions for improvements are welcome!

# Contributing

If you'd like to contribute to this project, please feel free to fork the repository and submit pull requests with your improvements.

# Installation

1. Clone the repository using `git clone https://github.com/sam-shepp/Snap_photos_import.git`
2. Install required libraries by running `pip install -r requirements.txt`
