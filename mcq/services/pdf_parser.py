import re
from pathlib import Path

import pymupdf


def clean_text(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def extract_pdf_pages(pdf_path):
    """
    Extract structured PDF information for the MCQ importer.

    Each page contains:
        - page dimensions
        - text blocks with coordinates
        - embedded images with coordinates

    No Django database records are created here.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(pdf_path)

    pages = []

    try:
        for page_number, page in enumerate(
            document,
            start=1,
        ):
            # ==========================================================
            # TEXT BLOCKS
            # ==========================================================

            raw_blocks = page.get_text("blocks")

            text_blocks = []

            for block in raw_blocks:
                if len(block) < 5:
                    continue

                x0, y0, x1, y1, text = block[:5]

                text = clean_text(text)

                if not text:
                    continue

                text_blocks.append(
                    {
                        "x0": float(x0),
                        "y0": float(y0),
                        "x1": float(x1),
                        "y1": float(y1),
                        "text": text,
                    }
                )

            text_blocks.sort(
                key=lambda item: (
                    round(item["y0"], 2),
                    round(item["x0"], 2),
                )
            )

            # ==========================================================
            # EMBEDDED IMAGES
            # ==========================================================

            images = []

            seen_xrefs = set()

            for image_index, image in enumerate(
                page.get_images(full=True),
                start=1,
            ):
                xref = image[0]

                # The same xref can occur more than once.
                if xref in seen_xrefs:
                    continue

                seen_xrefs.add(xref)

                rects = page.get_image_rects(
                    xref
                )

                for rect in rects:
                    images.append(
                        {
                            "image_index": image_index,
                            "xref": xref,
                            "x0": float(rect.x0),
                            "y0": float(rect.y0),
                            "x1": float(rect.x1),
                            "y1": float(rect.y1),
                            "width": float(rect.width),
                            "height": float(rect.height),
                        }
                    )

            images.sort(
                key=lambda item: (
                    round(item["y0"], 2),
                    round(item["x0"], 2),
                )
            )

            pages.append(
                {
                    "page_number": page_number,
                    "width": float(page.rect.width),
                    "height": float(page.rect.height),
                    "text_blocks": text_blocks,
                    "images": images,
                }
            )

    finally:
        document.close()

    return pages