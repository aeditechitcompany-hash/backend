from PIL import Image, ImageDraw
from pathlib import Path

source = Path("temp_set24_images/page_7_image_1_xref_65.jpeg")
out_dir = Path("temp_set24_q23_options")
out_dir.mkdir(exist_ok=True)

im = Image.open(source).convert("RGB")
w, h = im.size
print("Original image size:", w, "x", h)

# Preview four equal-width columns from the composite image.
for i in range(4):
    left = round(i * w / 4)
    right = round((i + 1) * w / 4)
    crop = im.crop((left, 0, right, h))
    crop.save(out_dir / f"Q23_option_{i+1}.jpg")
    print(f"Option {i+1}: x={left} to {right}")

# Make a larger preview for easier visual inspection.
files = [out_dir / f"Q23_option_{i}.jpg" for i in range(1, 5)]
thumbs = []
for f in files:
    img = Image.open(f).convert("RGB")
    img.thumbnail((300, 220))
    thumbs.append((f.name, img.copy()))

sheet = Image.new("RGB", (640, 4 * 270), "white")
draw = ImageDraw.Draw(sheet)
for i, (name, img) in enumerate(thumbs):
    y = i * 270
    draw.text((10, y + 5), name, fill="black")
    sheet.paste(img, (10, y + 30))

sheet.save(out_dir / "Q23_options_preview.jpg")
print("Preview saved to:", out_dir / "Q23_options_preview.jpg")
