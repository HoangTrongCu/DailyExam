"""Math engine tests."""

import pytest

from app.math_engine import MathEngineError, is_valid_number, numbers_equal, parse_number


class TestParse:
    def test_int(self): assert float(parse_number("42")) == 42
    def test_neg(self): assert float(parse_number("-7.25")) == -7.25
    def test_fraction(self): assert float(parse_number("1/2")) == 0.5
    def test_decimal(self): assert float(parse_number("0.5")) == 0.5
    def test_percent(self): assert float(parse_number("50%")) == 0.5
    def test_whitespace(self): assert float(parse_number("  3  ")) == 3
    def test_empty(self):
        with pytest.raises(MathEngineError): parse_number("")
    def test_empty_percent(self):
        with pytest.raises(MathEngineError): parse_number("%")
    def test_nonstring(self):
        with pytest.raises(MathEngineError): parse_number(42)
    def test_symbol(self):
        with pytest.raises(MathEngineError): parse_number("x + 1")
    def test_garbage(self):
        with pytest.raises(MathEngineError): parse_number("not a number")
    def test_infinity(self):
        with pytest.raises(MathEngineError): parse_number("oo")


class TestEqual:
    def test_identical(self): assert numbers_equal("27", "27")
    def test_different(self): assert not numbers_equal("27", "28")
    def test_fraction_eq_decimal(self): assert numbers_equal("1/2", "0.5")
    def test_percent_eq_decimal(self): assert numbers_equal("50%", "0.5")
    def test_ws(self): assert numbers_equal(" 42 ", "42")
    def test_invalid_student(self): assert not numbers_equal("abc", "42")
    def test_invalid_correct(self): assert not numbers_equal("42", "abc")
    def test_tolerance(self): assert numbers_equal("1.0000001", "1.0")


class TestValid:
    def test_valid(self): assert is_valid_number("3.14")
    def test_invalid(self): assert not is_valid_number("abc")
    def test_empty(self): assert not is_valid_number("")
