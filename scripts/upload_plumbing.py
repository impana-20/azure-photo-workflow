import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings


# Local extracted ZIP folder
LOCAL_FOLDER = Path(r"C:\Users\Impana S\Downloads\Azure_Plumbing_Image_Upload_Project (1)\data_collection\Electrical")

# Azure details
CONTAINER_NAME = "nivora"

# Exact destination shown in Azure Portal
AZURE_FOLDER = "Nivora Products/categories/Electrical"

# Image formats to upload
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


# Get Azure connection string
connection_string = os.environ.get(
    "AZURE_STORAGE_CONNECTION_STRING"
)

if not connection_string:
    raise ValueError(
        "Azure connection string not found."
    )


# Connect to Azure
blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)

container_client = blob_service_client.get_container_client(
    CONTAINER_NAME
)


# Check local folder
if not LOCAL_FOLDER.exists():
    raise FileNotFoundError(
        f"Folder not found: {LOCAL_FOLDER.resolve()}"
    )


uploaded = 0
skipped = 0


print("Starting Plumbing image upload...\n")


# Recursively find files
for file_path in LOCAL_FOLDER.rglob("*"):

    if not file_path.is_file():
        continue

    # Skip desktop.ini and other non-image files
    if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
        skipped += 1
        continue

    # Preserve UPVC and all subfolders
    relative_path = file_path.relative_to(LOCAL_FOLDER)

    blob_path = (
        f"{AZURE_FOLDER}/"
        f"{relative_path.as_posix()}"
    )

    # Set correct content type
    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }[file_path.suffix.lower()]

    print(f"Uploading: {file_path}")
    print(f"Azure: {blob_path}")

    with open(file_path, "rb") as data:

        container_client.upload_blob(
            name=blob_path,
            data=data,
            overwrite=True,
            content_settings=ContentSettings(
                content_type=content_type
            )
        )

    uploaded += 1


print("\n==============================")
print("Upload completed successfully!")
print(f"Images uploaded: {uploaded}")
print(f"Non-image files skipped: {skipped}")
print("==============================")

print(
    "\nUploaded to:"
    f"\n{CONTAINER_NAME}/{AZURE_FOLDER}"
)