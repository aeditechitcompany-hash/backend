from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

old = [
    '            if re.search(\n',
    '                r"[????????]",\n',
    '                remainder,\n',
    '            ):\n',
    '                parsed = split_options(remainder)\n',
    '\n',
    '                for option_number, option_text in parsed.items():\n',
    '                    options[option_number] = option_text\n',
    '                    last_option_number = option_number\n',
    '\n',
    '                continue\n',
]

new = [
    '            if re.search(\n',
    '                r"[????????]",\n',
    '                remainder,\n',
    '            ):\n',
    '                option_match = re.search(\n',
    '                    r"[????????]",\n',
    '                    remainder,\n',
    '                )\n',
    '\n',
    '                if option_match:\n',
    '                    before_options = clean_text(\n',
    '                        remainder[:option_match.start()]\n',
    '                    )\n',
    '\n',
    '                    if before_options:\n',
    '                        question_parts.append(before_options)\n',
    '\n',
    '                parsed = split_options(remainder)\n',
    '\n',
    '                for option_number, option_text in parsed.items():\n',
    '                    options[option_number] = option_text\n',
    '                    last_option_number = option_number\n',
    '\n',
    '                continue\n',
]

text = ''.join(lines)

old_text = ''.join(old)
new_text = ''.join(new)

if old_text not in text:
    raise SystemExit(
        "ERROR: Target block was not found. No file was changed."
    )

text = text.replace(old_text, new_text, 1)

path.write_text(text, encoding="utf-8", newline="")

print("SUCCESS: Updated numbered-question option handling.")
