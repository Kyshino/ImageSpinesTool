import os
import hashlib
from PIL import Image
from typing import List, Tuple

def calculate_image_hash(image_path: str) -> str:
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img_bytes = img.tobytes()
            return hashlib.sha256(img_bytes).hexdigest()
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return None

def find_duplicate_images(directory: str) -> List[Tuple[str, str]]:
    hashes = {}
    duplicates = []
    total_images = 0
    processed_images = 0
    
    print(f"\nSearching for duplicate images in: {directory}")
    
    for root, _, files in os.walk(directory):
        total_images += sum(1 for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')))
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                file_path = os.path.join(root, file)
                processed_images += 1
                
                print(f"\rProcessing: {processed_images}/{total_images} images... ", end="")
                
                image_hash = calculate_image_hash(file_path)
                if image_hash:
                    if image_hash in hashes:
                        duplicates.append((file_path, hashes[image_hash]))
                    else:
                        hashes[image_hash] = file_path
    
    print("\n")
    return duplicates

if __name__ == "__main__":
    while True:
        directory = input("Enter the directory path to search for duplicates: ").strip()
        
        if os.path.exists(directory):
            break
        else:
            print(f"Error: Directory '{directory}' does not exist. Please try again.")
    
    duplicates = find_duplicate_images(directory)

    if duplicates:
        print(f"Found {len(duplicates)} duplicate images:")
        for dup in duplicates:
            print(f"Duplicate: {dup[0]} <-> Original: {dup[1]}")
            os.remove(dup[0])
            print(f"File deleted: {dup[0]}")
    else:
        print("No duplicate images found.") 