# CLAUDE.md

Instructions for working in this Python project. I am explicitly engaging you, Claude, to follow **all** of these rules whenever you touch this repository. They are requirements, not suggestions.

## 1. Use `uv` for everything

Never use `pip`, `venv`, `poetry`, or `conda`. Never activate `.venv` manually and never edit `requirements.txt` or `pyproject.toml` dependency lists by hand.

| Task | Command |
|---|---|
| Create the env (only if `.venv/` is missing) | `uv venv` |
| Run anything (scripts, tests, linters) | `uv run python main.py`, `uv run pytest` |
| Add a dependency | `uv add <pkg>` / `uv add --dev <pkg>` |
| Remove a dependency | `uv remove <pkg>` |
| Upgrade | `uv lock --upgrade[-package <pkg>]` then `uv sync` |
| Sync env after pulling changes | `uv sync` |
| **Regenerate `requirements.txt` after ANY dependency change** | `uv export --no-hashes --format requirements-txt > requirements.txt` |

`pyproject.toml` + `uv.lock` are the source of truth; `requirements.txt` is a generated export.

## 2. Split code across multiple `.py` files

One responsibility per file, named for what it does (`models.py`, `utils.py`, `config.py`, `main.py`). Create new files as soon as a logical grouping appears — never let everything pile into one file. Keep the entry point focused on orchestration.

## 3. Document with docstrings only

Documentation goes **only** at the start of functions and classes, as multi-line `"""` docstrings. No `#` comments explaining lines, and no comments inside function bodies — clear naming should carry the rest.

```python
def divide_numbers(dividend, divisor):
    """Divide two numbers and return the float result.

    Args:
        dividend (int or float): The number to be divided.
        divisor (int or float): The number to divide by.

    Returns:
        float: The calculated quotient.

    Raises:
        ZeroDivisionError: If the divisor is zero.
    """
    return dividend / divisor
```

```python
class MyClass:
    """A one-sentence summary of the class's purpose.

    More detailed explanation of the class behaviors,
    state, and overall responsibilities.
    """

    def __init__(self, value):
        # Initialize the instance with a starting value
        self.value = value
```

Do **not** write this:

```python
def divide_numbers(dividend, divisor):  # divides numbers
    if divisor == 0:  # avoid divide by zero
        raise ZeroDivisionError()  # error out
    return dividend / divisor  # return result
```
## 4. Task completion
Once an edit is made and matches the request, state what changed and stop.
Do not re-read the file, re-run checks, or narrate additional verification
passes unless a command actually errors or a test fails.

## 5. Dont use GIT
**Dont touch use or view git**
**pretend that its not there at all**