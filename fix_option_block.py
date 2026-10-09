from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

lines = path.read_text(encoding="utf-8").splitlines()

# Current branch starts at line 689 and ends at line 696.
replacement = [
    '        if is_option_block(text):',
    '            option_match = re.search(',
    '                r"[\\u2460\\u2780\\u2461\\u2781\\u2462\\u2782\\u2463\\u2783]",',
    '                text,',
    '            )',
    '',
    '            if option_match:',
    '                before_options = clean_text(',
    '                    text[:option_match.start()]',
    '                )',
    '',
    '                if before_options:',
    '                    question_parts.append(before_options)',
    '',
    '            parsed = split_options(text)',
    '',
    '            for option_number, option_text in parsed.items():',
    '                options[option_number] = option_text',
    '                last_option_number = option_number',
    '',
    '            continue',
]

# Lines 689-696 are indexes 688-695.
lines[688:696] = replacement

path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("SUCCESS: Updated option-block handling.")
