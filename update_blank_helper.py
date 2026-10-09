from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

text = path.read_text(encoding="utf-8")

start_marker = "def restore_blank_marker(question_number, text):"
end_marker = "\ndef extract_question_number(text):"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit(
        "ERROR: restore_blank_marker() was not found. "
        "No file was changed."
    )

new_function = '''def restore_blank_marker(question_number, text):
    """
    Restore the visual blank position for questions where the
    PDF text layer does not contain an explicit blank marker.

    This is specific to the current PDF.
    """

    if not text:
        return text

    if question_number == 11:
        text = re.sub(
            r"???\\s+??\\s+?????????\\.",
            "??? ?? [BLANK] ?????????.",
            text,
        )

    if question_number == 12:
        text = re.sub(
            r"???\\s+??????",
            "??? [BLANK] ??????",
            text,
        )

    if question_number == 13:
        text = re.sub(
            r"?????????\\s+???????\\.",
            "????????? [BLANK] ???????.",
            text,
        )

    return text
'''

text = text[:start] + new_function + text[end:]

path.write_text(
    text,
    encoding="utf-8",
)

print("Updated restore_blank_marker() for the actual PDF text.")
