import sys
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image

NORMAL_MAX_BYTES = 10 * 1024 * 1024
AGGRESSIVE_MAX_BYTES = 5 * 1024 * 1024
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_file_size(path):
    return os.path.getsize(path)


def downscale_image(input_path, max_bytes):
    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        return None

    file_size = get_file_size(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_ext = ext.lower() if ext.lower() in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"
    output_path = os.path.join(OUTPUT_DIR, f"{name}_downscaled{output_ext}")

    img = Image.open(input_path)

    if img.mode == "RGBA" and output_ext in (".jpg", ".jpeg"):
        img = img.convert("RGB")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    if file_size <= max_bytes:
        img.save(output_path, quality=95)
        print(f"Image already under limit. Saved to: {output_path}")
        return output_path

    quality = 95
    scale = 1.0

    img.save(output_path, quality=quality, optimize=True)

    while get_file_size(output_path) > max_bytes and quality > 20:
        quality -= 5
        img.save(output_path, quality=quality, optimize=True)

    if get_file_size(output_path) <= max_bytes:
        print(f"Downscaled (quality={quality}): {output_path}")
        return output_path

    while get_file_size(output_path) > max_bytes and scale > 0.1:
        scale -= 0.1
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        resized = img.resize((new_width, new_height), Image.LANCZOS)
        resized.save(output_path, quality=quality, optimize=True)

    print(f"Downscaled (quality={quality}, scale={scale:.0%}): {output_path}")
    return output_path


def pick_images():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()
    paths = filedialog.askopenfilenames(
        title="Select images to downscale",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return paths


def pick_mode():
    print("Select downscale mode:")
    print("  1) Normal     - 10MB or less")
    print("  2) Aggressive -  5MB or less")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "2":
        return AGGRESSIVE_MAX_BYTES
    return NORMAL_MAX_BYTES


if __name__ == "__main__":
    max_bytes = pick_mode()

    if len(sys.argv) >= 2:
        files = sys.argv[1:]
    else:
        files = pick_images()

    if not files:
        print("No images selected.")
        sys.exit(0)

    for path in files:
        downscale_image(path, max_bytes)