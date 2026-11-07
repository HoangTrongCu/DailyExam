"""SymPy-powered safe number parser + comparator."""

import sympy


class MathEngineError(ValueError):
    pass


def parse_number(expression: str) -> sympy.Expr:
    if not isinstance(expression, str):
        raise MathEngineError("not a string")
    cleaned = expression.strip()
    if not cleaned:
        raise MathEngineError("empty")
    if cleaned.endswith("%"):
        inner = cleaned[:-1].strip()
        if not inner:
            raise MathEngineError("empty percent")
        return _sympify(inner) / 100
    return _sympify(cleaned)


def _sympify(text: str) -> sympy.Expr:
    try:
        expr = sympy.sympify(text, evaluate=True)
    except (sympy.SympifyError, SyntaxError, TypeError) as exc:
        raise MathEngineError(f"cannot parse: {text!r}") from exc
    if not isinstance(expr, sympy.Expr) or not expr.is_number:
        raise MathEngineError(f"not a number: {text!r}")
    if expr.is_infinite or expr.has(sympy.nan):
        raise MathEngineError(f"non-finite: {text!r}")
    return expr


def numbers_equal(student: str, correct: str, tolerance: float = 1e-6) -> bool:
    try:
        s = parse_number(student)
        c = parse_number(correct)
    except MathEngineError:
        return False
    return abs(float(s) - float(c)) < tolerance


def is_valid_number(expression: str) -> bool:
    try:
        parse_number(expression)
        return True
    except MathEngineError:
        return False
