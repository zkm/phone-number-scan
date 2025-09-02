import os
import sys

# Ensure the src/ folder is on sys.path for tests (when package isn't installed)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from phone_number_scan import convert_letters_to_numbers, build_vanity_regex


def test_convert_letters_to_numbers():
    assert convert_letters_to_numbers('GET-CASH') == '438-2274'


def test_build_vanity_regex_simple():
    rx = build_vanity_regex('1-866-GET-CASH')
    assert '866' in rx
