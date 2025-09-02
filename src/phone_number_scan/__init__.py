"""phone_number_scan package

Public API: convert_letters_to_numbers, build_vanity_regex, scan_and_update_files, write_results, main
"""
from __future__ import annotations

import re
import os
import csv
import logging
from typing import Iterable, List, Dict, Optional

LETTER_TO_NUM = {
    'A': '2', 'B': '2', 'C': '2',
    'D': '3', 'E': '3', 'F': '3',
    'G': '4', 'H': '4', 'I': '4',
    'J': '5', 'K': '5', 'L': '5',
    'M': '6', 'N': '6', 'O': '6',
    'P': '7', 'Q': '7', 'R': '7', 'S': '7',
    'T': '8', 'U': '8', 'V': '8',
    'W': '9', 'X': '9', 'Y': '9', 'Z': '9'
}


def convert_letters_to_numbers(phone_number: str) -> str:
    """Convert vanity letters to digits in a phone number string.

    Letters are mapped using a standard telephone keypad mapping. Non-letters
    (digits and punctuation) are preserved.
    """
    return ''.join(LETTER_TO_NUM.get(c.upper(), c) for c in phone_number)


def format_phone_number(phone_number: str, region: str = "US") -> str:
    """Attempt to format phone numbers using phonenumbers if available.

    Falls back to returning the input string when the library is not present.
    """
    try:
        from phonenumbers import parse, format_number, PhoneNumberFormat
        parsed = parse(phone_number, region)
        return format_number(parsed, PhoneNumberFormat.NATIONAL)
    except Exception:
        return phone_number


def build_vanity_regex(vanity: str) -> str:
    """Build a forgiving regex that matches the vanity format or its numeric equivalent.

    The function tolerates common separators (spaces, dots, dashes, parentheses).
    """
    parts = re.split(r"[-\s]+", vanity.upper())
    if len(parts) < 3:
        raise ValueError("Vanity number must contain at least 3 groups (country, area, rest)")

    area = parts[1] if len(parts) > 1 else ""
    exchange = parts[2] if len(parts) > 2 else ""
    line = parts[3] if len(parts) > 3 else parts[-1]
    numeric_line = convert_letters_to_numbers(line)

    def build_pattern(a: str, ex: str, ln: str) -> str:
        return (
            r"(?:\+?1[\s.-]?)?"
            + r"(?:\(?" + re.escape(a) + r"\)?[\s.-]?)"
            + re.escape(ex) + r"[\s.-]?"
            + re.escape(ln)
        )

    pattern_vanity = build_pattern(area, exchange, line)
    pattern_numeric = build_pattern(area, exchange, numeric_line)

    return f"(?:{pattern_vanity})|(?:{pattern_numeric})"


def scan_and_update_files(
    search_dir: str,
    vanity: str,
    extensions: Optional[Iterable[str]] = None,
    include_pdf: bool = False,
    region: str = "US",
) -> List[Dict[str, object]]:
    """Scan files under search_dir for the vanity number and return result rows.

    Returns a list of dicts with keys: File Path, Original Matches, Converted Numbers, Count
    """
    if extensions is None:
        extensions = ['.jsp', '.txt', '.html', '.md']

    regex = build_vanity_regex(vanity)
    results: List[Dict[str, object]] = []

    # Try optional PDF support lazily
    pdf_support = False
    try:
        import fitz  # PyMuPDF
        pdf_support = True
    except Exception:
        pdf_support = False

    for root, _, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            try:
                text = ""
                if ext in extensions:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                elif ext == '.pdf' and include_pdf and pdf_support:
                    with fitz.open(file_path) as doc:
                        for page in doc:
                            text += page.get_text()
                else:
                    continue

                matches = re.findall(regex, text, re.IGNORECASE)
                updated_numbers: List[str] = []

                for match in matches:
                    match_str = match
                    numeric = convert_letters_to_numbers(match_str)
                    formatted = format_phone_number(numeric, region=region)
                    updated_numbers.append(formatted)

                if updated_numbers:
                    results.append({
                        "File Path": file_path,
                        "Original Matches": ", ".join(matches),
                        "Converted Numbers": ", ".join(updated_numbers),
                        "Count": len(updated_numbers)
                    })

                logging.info("Processed: %s (%d matched)", file_path, len(updated_numbers))

            except Exception:
                logging.warning("Error processing %s", file_path)
                continue

    return results


def write_results(results: List[Dict[str, object]], output_file: str) -> Optional[str]:
    """Try to write results to Excel (pandas) or fall back to CSV. Returns path or None if empty."""
    if not results:
        return None

    try:
        import pandas as pd
        df = pd.DataFrame(results)
        if output_file.lower().endswith('.xlsx'):
            df.to_excel(output_file, index=False)
        else:
            df.to_csv(output_file, index=False)
        return output_file
    except Exception:
        keys = list(results[0].keys())
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        return output_file


def parse_args(argv: Optional[Iterable[str]] = None):
    import argparse
    p = argparse.ArgumentParser(description="Scan files for vanity phone numbers and convert them to digits.")
    p.add_argument('--search-dir', '-d', default='.', help='Directory to scan (default: current directory)')
    p.add_argument('--target-vanity', '-t', required=True, help='Vanity number to search for (e.g. "1-866-290-HELP")')
    p.add_argument('--output-file', '-o', default='vanity_matches.csv', help='Output file path (xlsx or csv)')
    p.add_argument('--extensions', '-e', nargs='*', help='File extensions to scan (e.g. .html .txt .jsp)')
    p.add_argument('--include-pdf', action='store_true', help='Attempt to scan PDF files (requires PyMuPDF)')
    p.add_argument('--region', default='US', help='Region code for phone number parsing (default: US)')
    p.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    return p.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(levelname)s: %(message)s')

    logging.info("Scanning '%s' for: %s", args.search_dir, args.target_vanity)
    results = scan_and_update_files(args.search_dir, args.target_vanity, extensions=args.extensions, include_pdf=args.include_pdf, region=args.region)

    if results:
        out_path = write_results(results, args.output_file)
        logging.info('Scan complete. Results saved to: %s', out_path)
        logging.info('Total files matched: %d', len(results))
        total_numbers = sum(r.get('Count', 0) for r in results)
        logging.info('Total numbers found: %d', total_numbers)
    else:
        logging.info('No vanity or numeric matches found.')


__all__ = [
    'convert_letters_to_numbers',
    'build_vanity_regex',
    'scan_and_update_files',
    'write_results',
    'main',
]
