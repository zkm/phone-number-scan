import os
import argparse

def make_test_files(test_dir):
    os.makedirs(test_dir, exist_ok=True)

    sample_files = {
    "contact.jsp": """
        Reach us at (800) 555-TEST (2024) or (212) 555-1234 (2023).
        Emergency? Call 1-888-NEW-CALL now.
    """,
    "info.txt": """
        Main office: 1-800-123-4567
        Support: (310) 222-HELP (2025)
        Fax: 213.555.1212
    """,
    "about.html": """
        <p>Contact Sales: 1-866-GET-CASH</p>
        <p>Tech Support: +1 (415) 555-0911</p>
    """,
    "readme.md": """
        This is a markdown file and should be ignored by the script.
        Call us: 1-234-567-8900
    """
}
    for filename, content in sample_files.items():
        with open(os.path.join(test_dir, filename), "w", encoding="utf-8") as f:
            f.write(content.strip())


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='Create small set of test files for phone scan.')
    p.add_argument('--test-dir', '-d', default='test_phone_files', help='Directory to create test files in')
    return p.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()
    make_test_files(args.test_dir)
    print(f"Test files created in '{args.test_dir}'")
