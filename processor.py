import os
import sys
import glob
import subprocess
import shutil
from PIL import Image
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
# Only use CREATE_NO_WINDOW on Windows
SUBPROCESS_KWARGS = {}
if sys.platform == "win32":
    SUBPROCESS_KWARGS["creationflags"] = subprocess.CREATE_NO_WINDOW


def process_image(main_path, overlay_path, output_path, log_callback):
    try:
        base_img = Image.open(main_path).convert("RGBA")
        overlay_img = Image.open(overlay_path).convert("RGBA")

        if base_img.size != overlay_img.size:
            overlay_img = overlay_img.resize(base_img.size, Image.Resampling.LANCZOS)

        combined = Image.alpha_composite(base_img, overlay_img)
        combined.convert("RGB").save(output_path, "JPEG", quality=95)
        log_callback(f"[*] Created image: {os.path.basename(output_path)}")
    except Exception as e:
        log_callback(f"[!] Error on image {os.path.basename(main_path)}: {e}")


def process_video(main_path, overlay_path, out_path, log_callback):
    log_callback(f"[*] Processing video: {os.path.basename(main_path)}...")

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

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            **SUBPROCESS_KWARGS,  # Safely applies on Windows, ignored on Mac/Linux
        )
        log_callback(f"[+] Finished: {os.path.basename(out_path)}")
    except subprocess.CalledProcessError as e:
        log_callback(
            f"[!] Error processing {os.path.basename(main_path)}: {e.stderr.decode('utf-8', errors='ignore')}"
        )
    except Exception as e:
        log_callback(f"Critical error: {e}")


def run_batch(input_dir, output_dir, log_callback):
    # 1. Find ALL main video and image files instead of overlays
    search_mp4 = glob.glob(os.path.join(input_dir, "*-main.mp4"))
    search_jpg = glob.glob(os.path.join(input_dir, "*-main.jpg"))
    search_jpeg = glob.glob(os.path.join(input_dir, "*-main.jpeg"))

    all_main_files = search_mp4 + search_jpg + search_jpeg

    if not all_main_files:
        log_callback(
            "No media files (*-main.mp4, *-main.jpg) found in the input directory."
        )
        return

    log_callback(f"Found {len(all_main_files)} media files. Starting processing...\n")

    for main_path in all_main_files:
        # Extract the base file name (e.g., remove "-main.mp4")
        file_name_with_ext = os.path.basename(main_path)
        name_only, ext = os.path.splitext(file_name_with_ext)
        base_name = name_only.replace("-main", "")

        # Define paths
        overlay_path = os.path.join(input_dir, f"{base_name}-overlay.png")
        out_path = os.path.join(output_dir, f"{base_name}-combined{ext}")

        # Skip if already in the output folder
        if os.path.exists(out_path):
            log_callback(f"[-] Skipping (already exists): {os.path.basename(out_path)}")
            continue

        # 2. Check if an overlay exists for this specific file
        if os.path.exists(overlay_path):
            if ext.lower() == ".mp4":
                process_video(main_path, overlay_path, out_path, log_callback)
            else:
                process_image(main_path, overlay_path, out_path, log_callback)
        else:
            # 3. No overlay found? Just copy the original file to the output folder
            try:
                shutil.copy2(main_path, out_path)
                log_callback(f"[*] Copied (no overlay): {os.path.basename(out_path)}")
            except Exception as e:
                log_callback(f"[!] Error copying {file_name_with_ext}: {e}")

    log_callback("\n=== Processing Complete! ===")
