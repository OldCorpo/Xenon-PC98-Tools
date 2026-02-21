#!/bin/python
#
# A script to insert the Xenon translations into .U.CC files 
# 
# Basically lookups for every 00 FD ?? marker (hexadecimal)
# And then tries to convert the substring to Shift-JIS
# If a match is found, replaces everything with the translation
# At the translation file.
#
# Althought it doesn't (still) catches some less standard lines
# where a 00 or 00 ?? marker is the terminator.
#

import re
import argparse
from pathlib import Path


def load_translations(filename):
    """
    Load translations into a dictionary:
    {
        "Japanese sentence": "English translation"
    }
    """
    translations = {}

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        if line.startswith("//"):
            japanese = line[2:]  # remove //
            if i + 1 < len(lines):
                english = lines[i + 1].rstrip("\n")
                translations[japanese] = english
                i += 2
            else:
                i += 1
        else:
            i += 1

    return translations


def process_file(input_file, translation_file, output_file):
    translations = load_translations(translation_file)

    with open(input_file, "rb") as f:
        data = f.read()

    # Regex pattern:
    # 00 FD followed by any byte
    pattern = re.compile(b'\x00\xFD(.)')

    output = bytearray()
    pos = 0

    matches = list(pattern.finditer(data))

    for i, match in enumerate(matches):
        start_marker = match.start()
        start_content = match.end()

        # Add everything before this marker
        if pos < start_marker:
            output.extend(data[pos:start_marker])

        # Add marker itself unchanged
        output.extend(data[start_marker:start_content])

        # Determine end of content (next marker or EOF)
        if i + 1 < len(matches):
            end_content = matches[i + 1].start()
        else:
            end_content = len(data)

        original_bytes = data[start_content:end_content]

        try:
            original_text = original_bytes.decode("shift_jis")
        except UnicodeDecodeError:
            # If it fails decoding, keep original
            output.extend(original_bytes)
            pos = end_content
            continue

        # Remove possible trailing null bytes
        stripped_text = original_text.rstrip('\x00')

        if stripped_text in translations:
            translated_text = translations[stripped_text]
            new_bytes = translated_text.encode("shift_jis", errors="replace")
            output.extend(new_bytes)
        else:
            # If no translation found, keep original
            output.extend(original_bytes)

        pos = end_content

    # Add remaining data
    if pos < len(data):
        output.extend(data[pos:])

    with open(output_file, "wb") as f:
        f.write(output)


# Main loop
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .U.CC script file.")

    parser.add_argument("input_file", help="Path to input file (on ../scripts_cc/)")

    # Optional named arguments with defaults
    parser.add_argument(
        "-t", "--translation",
        default="../translation/_script-japanese.txt",
        help="Path to translation file. Default: (../translation/_script-japanese.txt)"
    )

    parser.add_argument(
        "-o", "--output",
        help="Optional output file. Default: (../scripts_merge/auto-generated)"
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if args.translation:
        translation_path = Path(args.translation)
    else:
        translation_path = "../translation/_script-japanese.txt"

    if args.output:
        output_path = Path(args.output)
    else:
        # Replace 'scripts_cc' directory with 'scripts_merge'
        output_path = input_path.parent.parent / "scripts_merge" / input_path.name

    process_file(input_path, translation_path, output_path)
