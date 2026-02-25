import re
import argparse
from pathlib import Path

verbose = False
extra_verbose = False


# ------------------------------------------------------------
# Translation Loader
# ------------------------------------------------------------

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
            japanese = line[2:]
            if i + 1 < len(lines):
                english = lines[i + 1].rstrip("\n")
                translations[japanese] = english
                i += 2
            else:
                i += 1
        else:
            i += 1

    return translations


# ------------------------------------------------------------
# Japanese Detection (Prevents Latin Matching)
# ------------------------------------------------------------

def contains_japanese(text: str) -> bool:
    """
    Returns True if string contains Japanese characters.
    Prevents matching pure Latin strings.
    """

    for ch in text:
        code = ord(ch)

        # Hiragana
        if 0x3040 <= code <= 0x309F:
            return True

        # Katakana
        if 0x30A0 <= code <= 0x30FF:
            return True

        # Kanji
        if 0x4E00 <= code <= 0x9FFF:
            return True

    return False


# ------------------------------------------------------------
# Shift-JIS Detection Helpers
# ------------------------------------------------------------

def is_valid_shift_jis_char(data: bytes, pos: int) -> int:
    """
    Returns:
        2  -> valid double-byte Shift-JIS
        1  -> valid single-byte Shift-JIS
        0  -> not Shift-JIS
    """

    if pos >= len(data):
        return 0

    b1 = data[pos]

    # ASCII
    if 0x20 <= b1 <= 0x7E:
        return 1

    # Half-width katakana
    if 0xA1 <= b1 <= 0xDF:
        return 1

    # Double-byte first byte
    if (0x81 <= b1 <= 0x9F) or (0xE0 <= b1 <= 0xFC):
        if pos + 1 < len(data):
            b2 = data[pos + 1]
            if 0x40 <= b2 <= 0xFC and b2 != 0x7F:
                return 2

    return 0


def extract_shift_jis_string(data: bytes, start: int):
    """
    Extract continuous Shift-JIS sequence starting at position.
    Returns (bytes_string, end_position)
    """

    pos = start
    collected = bytearray()

    while pos < len(data):
        size = is_valid_shift_jis_char(data, pos)

        if size == 0:
            break

        collected.extend(data[pos:pos + size])
        pos += size

    return bytes(collected), pos


# ------------------------------------------------------------
# Core Binary Processor
# ------------------------------------------------------------

def process_binary_stream(data: bytes, translations: dict) -> bytes:
    """
    Walk byte-by-byte through file:
    - Detect Shift-JIS sequences
    - Match against dictionary
    - Replace safely
    - Preserve leading garbage character
    - Never overwrite unrelated bytes
    """

    output = bytearray()
    pos = 0

    while pos < len(data):

        size = is_valid_shift_jis_char(data, pos)

        # Not Shift-JIS → copy raw byte
        if size == 0:
            output.append(data[pos])
            pos += 1
            continue

        # Extract candidate string
        sjis_bytes, end_pos = extract_shift_jis_string(data, pos)

        try:
            decoded = sjis_bytes.decode("shift_jis")
        except UnicodeDecodeError:
            output.extend(sjis_bytes)
            pos = end_pos
            continue

        # Debug print for detected strings
        if verbose and len(decoded) > 10:
            print("Detected:", decoded)

        # Skip pure Latin strings
        if not contains_japanese(decoded):
            output.extend(sjis_bytes)
            pos = end_pos
            continue

        # ----------------------------------------------------
        # Direct match
        # ----------------------------------------------------
        if decoded in translations:
            if verbose:
                print(f"[MATCH] {decoded}")

            new_bytes = translations[decoded].encode("shift_jis")
            output.extend(new_bytes)
            pos = end_pos
            continue

        # ----------------------------------------------------
        # Trimmed match (preserve leading garbage byte)
        # ----------------------------------------------------
        if len(decoded) > 1:
            trimmed = decoded[1:]

            if contains_japanese(trimmed) and trimmed in translations:
                if verbose:
                    print(f"[MATCH-TRIMMED] {trimmed}")

                # Preserve first original byte
                output.append(sjis_bytes[0])

                new_bytes = translations[trimmed].encode("shift_jis")
                output.extend(new_bytes)
                pos = end_pos
                continue

        # No match → copy original
        output.extend(sjis_bytes)
        pos = end_pos

    return bytes(output)


# ------------------------------------------------------------
# File Processor
# ------------------------------------------------------------

def process_file(input_file, translation_file, output_file):
    translations = load_translations(translation_file)

    with open(input_file, "rb") as f:
        data = f.read()

    processed = process_binary_stream(data, translations)

    with open(output_file, "wb") as f:
        f.write(processed)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Shift-JIS safe binary string replacer."
    )

    parser.add_argument("input_file", help="Path to input raw file")

    parser.add_argument(
        "-t", "--translation",
        default="../translation/_script-japanese.txt",
        help="Translation file"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "-vv", "--extra-verbose",
        action="store_true",
        help="Extra verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        verbose = True

    if args.extra_verbose:
        extra_verbose = True
        verbose = True

    input_path = Path(args.input_file)
    translation_path = Path(args.translation)

    '''
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".translated")
    '''

    if args.output:
        output_path = Path(args.output)
    else:
        # Replace 'scripts_cc' directory with 'scripts_merge'
        output_path = input_path.parent.parent / "scripts_merge" / input_path.name

    # Temp path
    temp_path = input_path.parent.parent / "scripts_steps" / input_path.name

    #process_file(input_path, translation_path, output_path)

    """
    - Process files
    """
    # Base pattern, 80% of the matches
    first_path = temp_path.with_name(temp_path.name + '.H1')
    process_file(input_path, translation_path, first_path)

    # 2nd pattern
    eleventh_path = temp_path.with_name(temp_path.name + '.H2')
    process_file(first_path, translation_path, output_path)


