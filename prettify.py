import json

def convert(input_file, output_file):
    """
    Convert a JSON file to a prettified version.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output prettified JSON file.
    """
    with open(input_file, 'r', encoding='utf8') as infile:
        data = json.load(infile)

    with open(output_file, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 3:
        print("Usage: python convert.py <input_file> <output_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Input file {input_file} does not exist.")
        sys.exit(1)

    convert(input_file, output_file)