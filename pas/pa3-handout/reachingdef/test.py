import os
import tempfile
import filecmp
import pytest

from reachingdef import main_logic


# List of (input_file, expected_output_file) pairs
test_cases = [
    ("tests/p1.txt", "tests/expected1.txt"),
    ("tests/p2.txt", "tests/expected2.txt"),
    ("tests/p3.txt", "tests/expected3.txt"),
    # Add more cases as needed
]

@pytest.mark.parametrize("input_file, expected_output_file", test_cases)
def test_main_logic(input_file, expected_output_file):
    # Create a temporary output file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        output_path = tmp.name

    try:
        # Run the main logic
        main_logic(input_file, output_path)

        # Read actual and expected outputs
        with open(output_path, 'r') as f:
            actual_lines = f.readlines()
        with open(expected_output_file, 'r') as f:
            expected_lines = f.readlines()

        # Compare contents ignoring order
        assert sorted(actual_lines) == sorted(expected_lines), \
            f"Output mismatch for input {input_file}"

    finally:
        # Clean up temp file
        if os.path.exists(output_path):
            os.remove(output_path)