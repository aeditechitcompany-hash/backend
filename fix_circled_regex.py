from pathlib import Path

path = Path(r"D:\nibangsh_app\backend\mcq\services\mcq_importer.py")

lines = path.read_text(encoding="utf-8").splitlines()

# Lines 660 and 664 are the two corrupted regex lines.
lines[659] = '                r"[\\u2460\\u2780\\u2461\\u2781\\u2462\\u2782\\u2463\\u2783]",'
lines[663] = '                    r"[\\u2460\\u2780\\u2461\\u2781\\u2462\\u2782\\u2463\\u2783]",'

path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("SUCCESS: Fixed the two circled-number regex lines.")
