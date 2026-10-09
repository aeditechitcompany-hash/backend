from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

lines = path.read_text(encoding="utf-8").splitlines()

replacement = [
    '            if re.search(',
    '                r"[????????]",',
    '                remainder,',
    '            ):',
    '                option_match = re.search(',
    '                    r"[????????]",',
    '                    remainder,',
    '                )',
    '',
    '                if option_match:',
    '                    before_options = clean_text(',
    '                        remainder[:option_match.start()]',
    '                    )',
    '',
    '                    if before_options:',
    '                        question_parts.append(before_options)',
    '',
    '                parsed = split_options(remainder)',
    '',
    '                for option_number, option_text in parsed.items():',
    '                    options[option_number] = option_text',
    '                    last_option_number = option_number',
    '',
    '                continue',
]

# Replace exactly the existing lines 659-669.
lines[658:669] = replacement

path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("SUCCESS: Numbered-question option handling updated.")
