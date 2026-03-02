#!/usr/bin/env python3

import argparse
import glob
import os
import string


def is_sjis_lead_byte(b):
    return (0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xEF)


def is_sjis_trail_byte(b):
    return (0x40 <= b <= 0x7E) or (0x80 <= b <= 0xFC)


def is_halfwidth_katakana(b):
    return 0xA1 <= b <= 0xDF


def latin_ratio(text):
    if not text:
        return 1.0

    latin_chars = sum(
        1 for c in text if c in string.ascii_letters or c in string.digits
    )
    return latin_chars / len(text)


DOT_CHARS = {'.', '。', '．', '・', '‥', '…'}


def dot_ratio(text):
    if not text:
        return 0.0

    dot_count = sum(1 for c in text if c in DOT_CHARS)
    return dot_count / len(text)


def scan_file(
    filepath,
    only_hex=False,
    only_text=False,
    min_length=4,
    max_latin_ratio=0.2,
    allow_dots=False,
    prev_bytes_count=3,
):

    with open(filepath, "rb") as f:
        data = f.read()

    i = 0
    size = len(data)

    while i < size:
        start = i
        buffer = bytearray()

        # Require FIRST character to be a double-byte SJIS char
        if (
            is_sjis_lead_byte(data[i])
            and i + 1 < size
            and is_sjis_trail_byte(data[i + 1])
        ):
            buffer.append(data[i])
            buffer.append(data[i + 1])
            i += 2
        else:
            i += 1
            continue

        # After the first double-byte char, allow normal continuation

        while i < size:
            b = data[i]

            if 0x20 <= b <= 0x7E:
                buffer.append(b)
                i += 1

            elif is_halfwidth_katakana(b):
                buffer.append(b)
                i += 1

            elif (
                is_sjis_lead_byte(b)
                and i + 1 < size
                and is_sjis_trail_byte(data[i + 1])
            ):
                buffer.append(b)
                buffer.append(data[i + 1])
                i += 2

            else:
                break

        if len(buffer) >= min_length:
            try:
                decoded = buffer.decode("shift_jis")

                '''
                if latin_ratio(decoded) > max_latin_ratio:
                    i = start + 1
                    continue

                if not allow_dots and dot_ratio(decoded) > 0.7:
                    i = start + 1
                    continue
                '''

                # Filter out Latin-heavy strings
                if latin_ratio(decoded) > max_latin_ratio:
                    continue

                # Dot-heavy filter
                if not allow_dots and dot_ratio(decoded) > 0.7:
                    i = start + 1
                    continue

                prev_start = max(0, start - prev_bytes_count)
                prev_bytes = data[prev_start:start]
                prev_hex = prev_bytes.hex().upper()

                if only_hex:
                    print(prev_hex)
                elif only_text:
                    print(decoded)
                else:
                    print(f"{prev_hex} | {decoded}")

            except UnicodeDecodeError:
                pass

        if start == i:
            i += 1



def main():
    parser = argparse.ArgumentParser(
        description="Scan raw files for Shift-JIS strings."
    )
    parser.add_argument("pattern", help="Glob pattern (e.g., '../*.U.CC')")
    parser.add_argument("--only-hex", action="store_true",
                        help="Output only previous 3 hex bytes")
    parser.add_argument("--only-text", action="store_true",
                        help="Output only Shift-JIS string")
    parser.add_argument("--min-length", type=int, default=4,
                        help="Minimum string length (default: 4)")
    parser.add_argument("--max-latin-ratio", type=float, default=0.2,
                        help="Discard string if Latin ratio exceeds this value (default: 0.2)")
    parser.add_argument("--allow-dots", action="store_true",
                        help="Allow dot-heavy strings like '..........'")
    parser.add_argument("-n", "--num-bytes", type=int, default=3,
                        help="Number of previous hex bytes to display (default: 3)")

    args = parser.parse_args()

    if args.only_hex and args.only_text:
        parser.error("Cannot use --only-hex and --only-text together.")

    files = glob.glob(args.pattern)
    if not files:
        print("No files matched.")
        return

    for filepath in files:
        if os.path.isfile(filepath):
            scan_file(
                filepath,
                only_hex=args.only_hex,
                only_text=args.only_text,
                min_length=args.min_length,
                max_latin_ratio=args.max_latin_ratio,
                allow_dots=args.allow_dots,
                prev_bytes_count=args.num_bytes
            )


if __name__ == "__main__":
    main()
