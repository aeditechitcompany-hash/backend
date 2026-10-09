from pathlib import Path

import pymupdf


def extract_pdf_images(pdf_path, output_dir):
    """
    Extract every embedded PDF image and save it as a PNG.

    Returns image metadata including:
        page number
        xref
        coordinates
        saved file
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = pymupdf.open(pdf_path)

    extracted = []

    try:

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            seen_xrefs = set()

            for image_index, image in enumerate(
                page.get_images(full=True),
                start=1,
            ):

                xref = image[0]

                # A PDF can reference the same image
                # more than once.
                if xref in seen_xrefs:
                    continue

                seen_xrefs.add(xref)

                rects = page.get_image_rects(
                    xref
                )

                if not rects:
                    continue

                image_data = document.extract_image(
                    xref
                )

                extension = image_data.get(
                    "ext",
                    "png",
                )

                image_bytes = image_data[
                    "image"
                ]

                filename = (
                    f"page_{page_number}"
                    f"_image_{image_index}"
                    f"_xref_{xref}."
                    f"{extension}"
                )

                output_path = (
                    output_dir / filename
                )

                output_path.write_bytes(
                    image_bytes
                )

                for rect in rects:

                    extracted.append(
                        {
                            "page_number": page_number,
                            "image_index": image_index,
                            "xref": xref,

                            "x0": rect.x0,
                            "y0": rect.y0,
                            "x1": rect.x1,
                            "y1": rect.y1,

                            "width": rect.width,
                            "height": rect.height,

                            "path": str(
                                output_path
                            ),
                        }
                    )

    finally:
        document.close()

    return extracted