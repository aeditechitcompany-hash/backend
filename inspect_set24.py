from pathlib import Path
from mcq.services.mcq_importer import extract_pdf_data, split_options

pdf_path = Path("media/mcq/imports/Full_set_24.pdf")
pages = extract_pdf_data(pdf_path)

print("PDF:", pdf_path.resolve())
print("PAGES:", len(pages))

for page in pages:
    print(f"\n{'=' * 25} PAGE {page['page_number']} {'=' * 25}")

    for block in page["text_blocks"]:
        text = block["text"]
        options = split_options(text)

        if options:
            print(
                f"OPTIONS y={block['y0']:.1f}: "
                f"{options}"
            )
        elif any(char.isdigit() for char in text[:5]):
            print(
                f"TEXT y={block['y0']:.1f}: "
                f"{text}"
            )

    for image in page["images"]:
        print(
            "IMAGE:",
            f"xref={image['xref']}",
            f"rect=({image['x0']:.1f}, {image['y0']:.1f}, "
            f"{image['x1']:.1f}, {image['y1']:.1f})",
        )
