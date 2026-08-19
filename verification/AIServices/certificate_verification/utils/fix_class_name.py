from pathlib import Path

# ===========================
# CONFIGURATION
# ===========================

FOLDER_PATH = r"../datasets/udemy"   # Change this
PREFIX = "udemy"                    # Change this

# ===========================

folder = Path(FOLDER_PATH)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}

files = [
    file for file in folder.iterdir()
    if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
]

files.sort()

for index, file in enumerate(files, start=1):
    new_name = f"{PREFIX}_{index:04d}{file.suffix.lower()}"

    new_path = folder / new_name

    print(f"{file.name}  -->  {new_name}")

    file.rename(new_path)

print(f"\nRenamed {len(files)} files successfully.")