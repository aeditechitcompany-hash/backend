from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


IMAGE_DIR = Path(
    r"D:\nibangsh_app\backend\temp_pdf_images"
)

OUTPUT = Path(
    r"D:\nibangsh_app\backend\mcq_image_sheet.jpg"
)


files = sorted(
    IMAGE_DIR.glob("*")
)


thumb_width = 180
thumb_height = 150
label_height = 35
columns = 4

rows = (
    len(files) + columns - 1
) // columns

sheet_width = (
    columns * thumb_width
)

sheet_height = (
    rows
    * (thumb_height + label_height)
)


sheet = Image.new(
    "RGB",
    (
        sheet_width,
        sheet_height,
        ),
    "white",
)

draw = ImageDraw.Draw(sheet)


for index, file_path in enumerate(files):

    try:

        image = Image.open(
            file_path
        ).convert("RGB")

        image.thumbnail(
            (
                thumb_width - 10,
                thumb_height - 10,
            )
        )

        x = (
            index % columns
        ) * thumb_width

        y = (
            index // columns
        ) * (
            thumb_height
            + label_height
        )

        image_x = (
            x
            + (
                thumb_width
                - image.width
            ) // 2
        )

        image_y = (
            y
            + (
                thumb_height
                - image.height
            ) // 2
        )

        sheet.paste(
            image,
            (
                image_x,
                image_y,
            ),
        )

        label = file_path.name

        draw.text(
            (
                x + 5,
                y + thumb_height,
            ),
            label,
            fill="black",
        )

    except Exception as exc:

        print(
            "Could not open:",
            file_path,
            exc,
        )


sheet.save(
    OUTPUT,
    quality=90,
)

print(
    "Created:",
    OUTPUT,
)