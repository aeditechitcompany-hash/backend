from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

text = path.read_text(encoding="utf-8")

old = '''    question_text = clean_text(
        " ".join(question_parts)
    )

    return {
        "question_text": question_text,
        "options": dict(sorted(options.items())),
    }
# ============================================================
'''

new = '''    question_text = clean_text(
        " ".join(question_parts)
    )

    question_text = restore_blank_marker(
        question_number,
        question_text,
    )

    return {
        "question_text": question_text,
        "options": dict(sorted(options.items())),
    }
# ============================================================
'''

if old not in text:
    raise SystemExit(
        "ERROR: Expected normal extraction block was not found. "
        "No file was changed."
    )

path.write_text(
    text.replace(old, new, 1),
    encoding="utf-8",
)

print("Connected restore_blank_marker() to normal question extraction.")
