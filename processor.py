import sys
import os
import glob
import subprocess
import shutil
from PIL import Image
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

SUBPROCESS_KWARGS = {}
if sys.platform == "win32":
    SUBPROCESS_KWARGS["creationflags"] = subprocess.CREATE_NO_WINDOW


def process_image(main_path, overlay_path, out_path):
    # 1. Open original image to extract its hidden EXIF metadata
    with Image.open(main_path) as base_orig:
        exif_data = base_orig.info.get("exif")

        with base_orig.convert("RGBA") as base_img:
            with Image.open(overlay_path).convert("RGBA") as overlay_img:
                if base_img.size != overlay_img.size:
                    overlay_img = overlay_img.resize(
                        base_img.size, Image.Resampling.LANCZOS
                    )

                combined = Image.alpha_composite(base_img, overlay_img)
                rgb_img = combined.convert("RGB")

                # 2. Save the new image, injecting the original EXIF data if it exists
                if exif_data:
                    rgb_img.save(out_path, quality=95, exif=exif_data)
                else:
                    rgb_img.save(out_path, quality=95)

    # 3. Force OS-level file creation/modification dates to match the original
    shutil.copystat(main_path, out_path)


def process_video(main_path, overlay_path, out_path):
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-i",
        main_path,
        "-i",
        overlay_path,
        "-filter_complex",
        "[0:v][1:v]overlay=0:0[v]",
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-map_metadata",
        "0",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "fast",
        "-c:a",
        "copy",
        out_path,
    ]
    subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        **SUBPROCESS_KWARGS,
    )

    # 3. Force OS-level file creation/modification dates to match the original
    shutil.copystat(main_path, out_path)


def run_batch(input_dir, output_dir, progress_callback, cancel_event=None):
    search_mp4 = glob.glob(os.path.join(input_dir, "*-main.mp4"))
    search_jpg = glob.glob(os.path.join(input_dir, "*-main.jpg"))
    search_jpeg = glob.glob(os.path.join(input_dir, "*-main.jpeg"))
    all_main_files = search_mp4 + search_jpg + search_jpeg

    total = len(all_main_files)
    if total == 0:
        progress_callback(0, 0, "No media files (*-main.*) found.")
        return

    progress_callback(0, total, f"Starting... Found {total} files")

    for i, main_path in enumerate(all_main_files, start=1):
        if cancel_event and cancel_event.is_set():
            progress_callback(i - 1, total, "Processing stopped by user.")
            return

        file_name = os.path.basename(main_path)
        name_only, ext = os.path.splitext(file_name)
        base_name = name_only.replace("-main", "")

        overlay_path = os.path.join(input_dir, f"{base_name}-overlay.png")
        out_path = os.path.join(output_dir, f"{base_name}-combined{ext}")

        if os.path.exists(out_path):
            progress_callback(i, total, f"Skipped (already exists): {file_name}")
            continue

        try:
            if os.path.exists(overlay_path):
                if ext.lower() == ".mp4":
                    process_video(main_path, overlay_path, out_path)
                else:
                    process_image(main_path, overlay_path, out_path)
                progress_callback(i, total, f"Processed: {file_name}")
            else:
                shutil.copy2(main_path, out_path)
                # shutil.copy2 automatically copies file timestamps/metadata
                progress_callback(i, total, f"Copied: {file_name}")
        except Exception as e:
            progress_callback(i, total, f"Error processing {file_name}: {e}")

    progress_callback(total, total, "Done! All files processed.")
