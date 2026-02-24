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
#

import re
import argparse
from pathlib import Path

verbose = False
extra_verbose = False

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

"""
Process by lines
"""

def process_line(line: bytes, translations: dict, base_pattern) -> bytes:
    """
    Processes one line:
    - Starts from beginning of line
    - Stops parsing at first terminator
    - Splits parsed region by terminators
    - Replaces Shift-JIS matches using translations dict
    - Rebuilds line losslessly
    """

    # Terminators
    terminator_pattern = re.compile(
        rb'(' +
        base_pattern +
        rb'|\xFD.|\x00|\x0C|\x04|\x05)'
    )

    match = terminator_pattern.search(line)

    # If no terminator found, write line untouched
    if not match:
        return line

    # Split line into:
    #   [processable_part] [terminator] [rest_of_line]
    start_terminator = match.start()
    end_terminator = match.end()

    processable_part = line[:start_terminator]
    terminator = line[start_terminator:end_terminator]
    rest_of_line = line[end_terminator:]

    # Now split processable_part by internal terminators
    split_pattern = re.compile(
        rb'(' +
        base_pattern +
        rb'|\xFD.|\x00|\x0C|\x04|\x05)'
    )

    parts = split_pattern.split(processable_part)
    rebuilt = bytearray()

    replaced_any = False

    for part in parts:

        if not part:
            continue

        # If it's a terminator, keep as-is
        if (
            re.fullmatch(base_pattern, part) or
            re.fullmatch(rb'\xFD.', part) or
            part in (b'\x00', b'\x0C', b'\x04', b'\x05')
        ):
            rebuilt.extend(part)
            continue

        # Try decoding as Shift-JIS
        try:
            decoded = part.decode("shift_jis")

            if decoded in translations:
                rebuilt.extend(
                    translations[decoded].encode("shift_jis")
                )
                replaced_any = True
            else:
                rebuilt.extend(part)

        except UnicodeDecodeError:
            rebuilt.extend(part)

    # If no replacements happened, return original line untouched
    if not replaced_any:
        return line

    # Rebuild full line
    final_line = rebuilt + terminator + rest_of_line
    return bytes(final_line)

def process_file_by_lines(input_file, translation_file, output_file, base_pattern):
    translations = load_translations(translation_file)

    with open(input_file, "rb") as f:
        lines = f.readlines()

    output = bytearray()

    for line in lines:
        processed = process_line(line, translations, base_pattern)
        output.extend(processed)

    with open(output_file, "wb") as f:
        f.write(output)
        

"""
Process by files
"""

def process_anomalous_string(data: bytes, translations: dict, base_pattern) -> bytes:
    """
    Processes raw binary data:
    - Splits by b'\x00\xFD??' and b'\x00'
    - Attempts Shift-JIS decoding on non-separator chunks
    - Replaces text if found in translations dict
    - Rebuilds and returns final bytes losslessly
    - Catching edge cases like b'\x00' b'\x0C' b'\x04' b'\x05'
    """

    # Pattern:
    # 00 FD ??   -> b'\x00\xFD.'
    # 00         -> b'\x00'
    #extra_patterns = rb'\x0C|\x04|\x05|\x00|\xFD.'
    #extra_patterns = rb'\x0C|\x04|\x05|\x00|\xFD'
    extra_patterns = rb'\x0C|\x04|\x05|\x00'


    new_pattern = rb'(' + base_pattern + rb'|' + extra_patterns + rb')'
    #pattern = re.compile(rb'(\x00\xFD.|\x0C|\x04|\x05|\x00)')
    pattern = re.compile(new_pattern)


    parts = pattern.split(data)
    rebuilt = bytearray()

    if verbose or extra_verbose:
        print(parts)
    
    for part in parts:
        if (
            #re.fullmatch(rb'\x00\xFD.', part) or 
            re.fullmatch(base_pattern, part) or 
            #re.fullmatch(rb'\x04\xFD.', part) or 
            #re.fullmatch(rb'\x0A\xFD.', part) or 
            re.fullmatch(rb'\xFD.', part) or 
            #part == b'\xFD' or
            part == b'\x00' or
            part == b'\x0C' or
            part == b'\x04' or
            part == b'\x05'
            ):

            rebuilt.extend(part)
            continue

        if not part:
            continue

        try:
            decoded = part.decode('shift_jis')

            if decoded in translations:
                new_bytes = translations[decoded].encode('shift_jis')
                rebuilt.extend(new_bytes)
            else:
                rebuilt.extend(part)

        except UnicodeDecodeError:
            rebuilt.extend(part)

    if extra_verbose:
        print()
        print(rebuilt)
        print()
        print()


    return bytes(rebuilt)


def process_file(input_file, translation_file, output_file, base_pattern):
    translations = load_translations(translation_file)

    with open(input_file, "rb") as f:
        data = f.read()

    # Regex pattern:
    # 00 FD followed by any byte
    #pattern = re.compile(b'\x00\xFD(.)')
    pattern = re.compile(base_pattern)

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
            # If it fails decoding, try harder
            processed_string = process_anomalous_string(original_bytes, translations, base_pattern)
            output.extend(processed_string)
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
            if extra_verbose:
                print(original_bytes)

        pos = end_content

    # Add remaining data
    if pos < len(data):
        output.extend(data[pos:])

    with open(output_file, "wb") as f:
        f.write(output)

if __name__ == "__main__":
    """
    Main loop
    - Preparing arguments to process the files
    - Otherwise fallback to defaults
    """
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

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Debug info is displayed."
    )

    parser.add_argument(
        "-vv", "--extra-verbose",
        action="store_true",
        help="Extra debug info is displayed."
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

    # Temp path
    temp_path = input_path.parent.parent / "scripts_steps" / input_path.name

    if args.verbose:
        verbose = True

    if args.extra_verbose:
        extra_verbose = True

    """
    - Process files
    """
    # Base pattern, 80% of the matches
    #first_pattern = b'\x00\xFD(.)'
    first_pattern = rb'\x00\xFD.'
    first_path = temp_path.with_name(temp_path.name + '.S1')
    process_file(input_path, translation_path, first_path, first_pattern)

    # 2nd pattern
    #second_pattern = rb'\x04\xFD.'
    second_pattern = rb'\x04\xFD.'
    second_path = temp_path.with_name(temp_path.name + '.S2')
    process_file(first_path, translation_path, second_path, second_pattern)

    # 3rd pattern
    third_pattern = rb'\x0F\xFD.'
    third_path = temp_path.with_name(temp_path.name + '.S3')
    process_file(second_path, translation_path, third_path, third_pattern)

    # 4th pattern
    fourth_pattern = rb'\x14\xFD.'
    fourth_path = temp_path.with_name(temp_path.name + '.S4')
    process_file(third_path, translation_path, fourth_path, fourth_pattern)

    # 5th pattern ## Process by lines only
    fifth_pattern = rb'^\x00'
    fifth_path = temp_path.with_name(temp_path.name + '.S5')
    process_file_by_lines(fourth_path, translation_path, fifth_path, fifth_pattern)

    # 6th pattern
    sixth_pattern = rb'\x0D\xFD.'
    sixth_path = temp_path.with_name(temp_path.name + '.S6')
    process_file(fifth_path, translation_path, sixth_path, sixth_pattern)

    # 7th pattern
    seventh_pattern = rb'\x26\xFD.'
    seventh_path = temp_path.with_name(temp_path.name + '.S7')
    process_file(sixth_path, translation_path, seventh_path, seventh_pattern)

    # 8th pattern
    eigth_pattern = rb'\x01\xFD.'
    eigth_path = temp_path.with_name(temp_path.name + '.S8')
    process_file(seventh_path, translation_path, eigth_path, eigth_pattern)

    # 9th pattern
    nineth_pattern = rb'\x40\xFD.'
    nineth_path = temp_path.with_name(temp_path.name + '.S9')
    process_file(eigth_path, translation_path, nineth_path, nineth_pattern)

    # 10th pattern
    tenth_pattern = rb'\x0A\xFD.'
    tenth_path = temp_path.with_name(temp_path.name + '.S10')
    process_file(nineth_path, translation_path, tenth_path, tenth_pattern)

    # 11th pattern
    eleventh_pattern = rb'\x46\xFD.'
    eleventh_path = temp_path.with_name(temp_path.name + '.S11')
    process_file(tenth_path, translation_path, output_path, eleventh_pattern)



