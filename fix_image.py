from PIL import Image
import os

# Compress msg1
print("Compressing msg1...")
img = Image.open('messages/msg1_original.jpg')
img = img.convert('RGB')
w, h = img.size
print(f"Original size: {w}x{h}")
if w > 1280 or h > 1280:
    ratio = min(1280/w, 1280/h)
    img = img.resize((int(w*ratio), int(h*ratio)), Image.Resampling.LANCZOS)
    print(f"Resized to: {int(w*ratio)}x{int(h*ratio)}")
img.save('messages/msg1.jpg', 'JPEG', quality=70, optimize=True)
size = os.path.getsize('messages/msg1.jpg') / 1024
print(f"msg1.jpg created: {size:.0f} KB")
print("Done!")


