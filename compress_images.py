"""
Compress images in the messages folder for faster Telegram uploads
"""
from PIL import Image
import os

MESSAGES_DIR = os.path.join(os.path.dirname(__file__), 'messages')
TARGET_SIZE_KB = 300  # Target size in KB
MAX_DIMENSION = 1280  # Max width/height

def compress_image(input_path, output_path, target_kb=300):
    """Compress image to target size"""
    img = Image.open(input_path)
    
    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if too large
    width, height = img.size
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        ratio = min(MAX_DIMENSION / width, MAX_DIMENSION / height)
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        print(f"  Resized: {width}x{height} -> {new_size[0]}x{new_size[1]}")
    
    # Try different quality levels to hit target size
    quality = 85
    while quality > 10:
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        size_kb = os.path.getsize(output_path) / 1024
        
        if size_kb <= target_kb:
            break
        quality -= 5
    
    return os.path.getsize(output_path) / 1024

def main():
    print("=" * 50)
    print("IMAGE COMPRESSOR")
    print("=" * 50)
    
    # Find all images
    for filename in os.listdir(MESSAGES_DIR):
        if filename.startswith('msg') and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_path = os.path.join(MESSAGES_DIR, filename)
            
            # Get original size
            original_size = os.path.getsize(input_path) / 1024
            
            # Create backup name
            name, ext = os.path.splitext(filename)
            backup_path = os.path.join(MESSAGES_DIR, f"{name}_original{ext}")
            compressed_path = os.path.join(MESSAGES_DIR, f"{name}.jpg")
            
            print(f"\n{filename}:")
            print(f"  Original size: {original_size:.1f} KB")
            
            if original_size <= TARGET_SIZE_KB:
                print(f"  Already small enough, skipping.")
                continue
            
            # Backup original (if not already backed up)
            if not os.path.exists(backup_path):
                os.rename(input_path, backup_path)
                print(f"  Backed up to: {os.path.basename(backup_path)}")
            
            # Always use backup as source for compression
            source_path = backup_path
            
            # Compress
            new_size = compress_image(source_path, compressed_path, TARGET_SIZE_KB)
            print(f"  Compressed: {new_size:.1f} KB")
            print(f"  Saved: {original_size - new_size:.1f} KB ({(1 - new_size/original_size)*100:.0f}% smaller)")

    print("\n" + "=" * 50)
    print("Done! Images compressed for faster uploads.")
    print("=" * 50)

if __name__ == '__main__':
    main()

