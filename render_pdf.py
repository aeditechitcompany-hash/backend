import pymupdf
from pathlib import Path

pdf_path = Path(r"D:\nibangsh_app\backend\Full set 1 F.pdf")
output_dir = Path(r"D:\nibangsh_app\backend\pdf_debug")

output_dir.mkdir(exist_ok=True)

doc = pymupdf.open(pdf_path)

for page_number in range(4, 8):  # PDF pages 5, 6, 7, 8
    page = doc[page_number]

    # High resolution for inspecting images/text
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)

    output_file = output_dir / f"page_{page_number + 1}.png"
    pix.save(output_file)

    print(f"Created: {output_file}")

doc.close()