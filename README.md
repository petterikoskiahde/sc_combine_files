# Snapchat Memory Combiner

A fast, fully offline, privacy-first desktop application designed to process exported Snapchat memories. It automatically merges your base media files (`-main.jpg` or `-main.mp4`) with their corresponding overlays (`-overlay.png`) to restore your memories to how they originally appeared on your device. 

Crucially, it preserves all original EXIF metadata (like GPS location and camera data) and operating system creation/modification timestamps.

## Features

* **Image & Video Support:** Processes both photos (JPG/JPEG) and videos (MP4) seamlessly.
* **Lossless Metadata Preservation:** Injects original EXIF data back into the combined images and retains original video metadata so your photo library timelines remain accurate.
* **Timestamp Preservation:** Matches the "Date Created" and "Date Modified" OS file timestamps of the output files to the original files.
* **100% Offline & Private:** Runs entirely on your local machine. No internet connection is required, no analytics are collected, and your personal data never leaves your computer.
* **Simple GUI:** Easy-to-use graphical interface with real-time progress tracking and a graceful stop button.
* **Cross-Platform:** Available as standalone executables for macOS and Windows via GitHub Actions.

## How It Works

When you request your data from Snapchat, memories with text, stickers, or filters are often exported as two separate files:
1. `[filename]-main.jpg` (or `.mp4`) - The base photo or video.
2. `[filename]-overlay.png` - The text, drawing, or filter with a transparent background.

This app scans your input folder for all `-main` files, finds the matching `-overlay` file, resizes it if necessary, and composites them together. The resulting file is saved as `[filename]-combined.jpg` (or `.mp4`) in your chosen output folder. If a memory doesn't have an overlay, the app simply copies the original file to the output folder to keep your archive complete.

## Usage (Pre-built Binaries)

You do not need to install Python or use the command line to use this app.

1. Download the latest release for your operating system (macOS or Windows) from the Releases page.
2. Extract the downloaded ZIP file.
3. Open the `Snapchat Memory Combiner` application.
4. Click **Browse...** next to the Input Folder and select the directory containing your unzipped Snapchat memories.
5. Click **Browse...** next to the Output Folder and select an empty directory where you want the combined files saved.
6. Click **Start Combining**. 

*Note: Because the app is an unsigned executable, Windows SmartScreen or macOS Gatekeeper may show an "Unrecognized app" warning. You can safely bypass this to run the application.*

## Development & Running from Source

If you prefer to run the app from the source code or want to contribute, follow these steps:

### Prerequisites
* Python 3.11 or higher
* `ffmpeg` (handled automatically via the `imageio-ffmpeg` package)

### Setup

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/snapchat-memory-combiner.git](https://github.com/yourusername/snapchat-memory-combiner.git)
   cd snapchat-memory-combiner
2. Install the required dependencies:
   ```bash
   pip install Pillow imageio-ffmpeg pyinstaller
3. Run the application::
   ```bash
   python app.py
