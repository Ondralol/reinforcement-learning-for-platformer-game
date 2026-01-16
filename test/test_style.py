import pytest
from pylint import epylint as lint

@pytest.mark.style
def test_code_style():
    """Test PEP8 compliance using Pylint"""

    # Run pylint on the src/ folder
    (pylint_stdout, pylint_stderr) = lint.py_run(
        "src --disable=C0301,C0103", return_std=True
    )

    # Read output
    output = pylint_stdout.getvalue()
    errors = [line for line in output.split("\n") if line.strip()]
    
    # Fail if any real issues are found
    assert not errors, f"Pylint found style issues:\n{output}"