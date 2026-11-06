"""Math engine — safe expression parsing and comparison using SymPy."""

from __future__ import annotations

import sympy


class MathEngineError(ValueError):
    """Raised when expression cannot be parsed safely."""


def parse_number(expression: str) -> sympy.Expr:
    """Parse a string into a SymPy numeric expression.

    Accepts: '1/2', '0.5', '50%', '  3 ', '-7.25'.
    Rejects: symbolic variables, function calls, infinity, nan.
    """
    if not isinstance(expression, str):
        raise MathEngineError("expression must be a string")

    cleaned = expression.strip()
    if not cleaned:
        raise MathEngineError("empty expression")

    if cleaned.endswith("%"):
        inner = cleaned[:-1].strip()
        if not inner:
            raise MathEngineError("empty percent")
        value = _sympify_number(inner)
        return value / 100

    return _sympify_number(cleaned)


def _sympify_number(text: str) -> sympy.Expr:
    try:
        expr = sympy.sympify(text, evaluate=True)
    except (sympy.SympifyError, SyntaxError, TypeError) as exc:
        raise MathEngineError(f"cannot parse: {text!r}") from exc

    if not isinstance(expr, sympy.Expr) or not expr.is_number:
        raise MathEngineError(f"expression is not a number: {text!r}")

    if expr.is_infinite or expr.has(sympy.nan):
        raise MathEngineError(f"non-finite value: {text!r}")

    return expr


def numbers_equal(student: str, correct: str, tolerance: float = 1e-6) -> bool:
    """Compare two numeric expressions within tolerance."""
    try:
        s = parse_number(student)
        c = parse_number(correct)
    except MathEngineError:
        return False

    diff = abs(float(s) - float(c))
    return diff < tolerance


def is_valid_number(expression: str) -> bool:
    """Return True if expression parses as a finite number."""
    try:
        parse_number(expression)
        return True
    except MathEngineError:
        return False
