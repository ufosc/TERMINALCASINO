# Tests

The tests use [pytest](https://docs.pytest.org/). From the repository root, `TERMINALCASINO/`, install the dependencies (pytest is included):

```shell
pip install -r requirements.txt
```

Then run the whole test suite:

```shell
python -m pytest
```

Some useful variations:

```shell
python -m pytest tests/test_poker.py         # a single file
python -m pytest tests/test_poker.py -v      # list each test by name
python -m pytest -k raise                    # only tests whose names contain "raise"
python -m pytest -rx                         # show the reason for each expected failure (xfail)
```

> **Note:** `python -m unittest discover tests` only finds `unittest.TestCase` classes, so it skips most of this suite. Use pytest.

Tests marked `@pytest.mark.xfail(strict=True)` document known bugs. They show up as `x` in the output. Once a bug is fixed, its test will start failing with `XPASS(strict)`. That means you should remove the marker.
