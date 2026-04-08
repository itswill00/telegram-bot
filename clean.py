import os
import re
import glob

def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    new_lines = []
    changed = False

    for line in lines:
        if "─" in line:
            changed = True
            continue  # remove horizontal rule lines

        # Match [ TEXT ] or [TEXT] where TEXT is all uppercase (plus spaces/ampersands)
        original_line = line
        line = re.sub(r'\[\s*([A-Z &]+)\s*\]', lambda m: m.group(1).title(), line)
        if line != original_line:
            changed = True

        new_lines.append(line)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"Cleaned {filepath}")

if __name__ == "__main__":
    search_dirs = [
        "handlers/**/*.py",
        "handlers/*.py"
    ]
    
    for pattern in search_dirs:
        for filepath in glob.glob(pattern, recursive=True):
            if os.path.isfile(filepath):
                clean_file(filepath)
