#!/usr/bin/env python3

import os
import sys
import shutil

# ====== CONFIGURATION ======

issue_string = {
    "今日も１人倒れた‥‥これで３人目だ。このままでは、我が調査隊は全滅してしまう。ヤツが来てからだ‥‥第１次調査隊の生き残りである、あいつが‥‥‥‥。":
    "Another one fell today... That makes three. At this rate, our entire expedition team will be wiped out. Ever since he arrived... That guy, the survivor from the First Expedition Team..."
}

# ============================


def print_help():
    print("Usage:")
    print("  python3 script.py <input_file> [output_file] [--verbose] [--help]")
    print("")
    print("Arguments:")
    print("  input_file     (required) Full path to source file")
    print("  output_file    (optional) Custom output file path")
    print("  --verbose      Enable detailed logging")
    print("  --help         Show this help message")
    sys.exit(0)


def main():
    verbose = False
    args = sys.argv[1:]

    if not args or "--help" in args:
        print_help()

    # Extract verbose flag
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

    if len(args) < 1:
        print("Error: input file required.")
        sys.exit(1)

    input_path = os.path.abspath(args[0])

    if not os.path.isfile(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    # Output path
    if len(args) >= 2:
        output_path = os.path.abspath(args[1])
    else:
        filename = os.path.basename(input_path)
        output_dir = os.path.abspath("../scripts_merge")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

    # Intermediate path
    intermediate_dir = os.path.abspath("../scripts_steps")
    os.makedirs(intermediate_dir, exist_ok=True)
    intermediate_path = os.path.join(
        intermediate_dir,
        os.path.basename(input_path) + ".D1"
    )

    if verbose:
        print(f"[+] Input file: {input_path}")
        print(f"[+] Intermediate file: {intermediate_path}")
        print(f"[+] Output file: {output_path}")

    # Create intermediate copy
    shutil.copy2(input_path, intermediate_path)

    if verbose:
        print("[+] Intermediate file created.")

    # Read binary data
    with open(intermediate_path, "rb") as f:
        data = f.read()

    original_data = data

    # Perform replacements
    for jp_text, en_text in issue_string.items():
        jp_bytes = jp_text.encode("shift_jis")
        en_bytes = en_text.encode("shift_jis")

        occurrences = data.count(jp_bytes)

        if occurrences == 0:
            print("[-] Warning: String not found in file.")
            continue

        if verbose:
            print(f"[+] Found {occurrences} occurrence(s).")
            print(f"[+] Original length: {len(jp_bytes)} bytes")
            print(f"[+] Replacement length: {len(en_bytes)} bytes")

        data = data.replace(jp_bytes, en_bytes)

    # Write final output
    with open(output_path, "wb") as f:
        f.write(data)

    if verbose:
        print("[+] Replacement complete.")
        print(f"[+] Output written to: {output_path}")
        print(f"[+] Size before: {len(original_data)} bytes")
        print(f"[+] Size after : {len(data)} bytes")

    print("Done.")


if __name__ == "__main__":
    main()
