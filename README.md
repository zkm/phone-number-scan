# Phone Number Scan

[![CI](https://github.com/zkm/phone-number-scan/actions/workflows/ci.yml/badge.svg)](https://github.com/zkm/phone-number-scan/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

![Python 3.10–3.12](https://img.shields.io/badge/Python-3.10%E2%80%933.12-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-5A5A5A)
![phonenumbers](https://img.shields.io/badge/phonenumbers-5A5A5A)

A small utility to scan a directory for vanity phone numbers (like 1-866-GET-HELP)
and convert them to their numeric equivalents. The script is generic and CLI-driven
so it can be used in different projects and published as a public repository.

## Setup (venv)

```bash
# create and activate a virtual environment (Linux/macOS, zsh)
python3 -m venv .venv
source .venv/bin/activate

# install dependencies and the package (editable)
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

## Quick start

```bash
# (optional) create some sample files to scan
python generate_test_files.py --test-dir test_phone_files

# run the CLI (after `pip install -e .` or `pip install .`)
phone-number-scan --search-dir test_phone_files --target-vanity "1-866-GET-CASH" --output-file results.csv

# alternatively, run as a module without installing
PYTHONPATH=src python -m phone_number_scan --search-dir test_phone_files --target-vanity "1-866-GET-CASH" --output-file results.csv
```

Notes:
- PDF scanning requires `PyMuPDF` (import `fitz`).
- The script will attempt to use `pandas` to write Excel files; otherwise it falls back to CSV.
- You can install dependencies for local runs with:

```bash
pip install -r requirements.txt
```

License: MIT
