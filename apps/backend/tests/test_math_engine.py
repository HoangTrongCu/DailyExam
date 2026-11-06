"""Tests for the math engine."""

import pytest

from app.math_engine import MathEngineError, is_valid_number, numbers_equal, parse_number


class TestParseNumber:
    def test_integer(self) -> None:
        assert float(parse_number("42")) == 42.0

    def test_negative(self) -> None:
        assert float(parse_number("-7.25")) == -7.25

    def test_fraction(self) -> None:
        assert float(parse_number("1/2")) == 0.5

    def test_decimal(self) -> None:
        assert float(parse_number("0.5")) == 0.5

    def test_percent(self) -> None:
        assert float(parse_number("50%")) == 0.5

    def test_percent_fraction(self) -> None:
        assert float(parse_number("25%")) == 0.25

    def test_whitespace_stripped(self) -> None:
        assert float(parse_number("  3  ")) == 3.0

    def test_empty_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number("   ")

    def test_empty_percent_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number("%")

    def test_non_string_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number(42)  # type: ignore[arg-type]

    def test_symbol_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number("x + 1")

    def test_garbage_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number("not a number")

    def test_infinity_raises(self) -> None:
        with pytest.raises(MathEngineError):
            parse_number("oo")


class TestNumbersEqual:
    def test_identical(self) -> None:
        assert numbers_equal("27", "27")

    def test_different(self) -> None:
        assert not numbers_equal("27", "28")

    def test_fraction_equals_decimal(self) -> None:
        assert numbers_equal("1/2", "0.5")

    def test_percent_equals_decimal(self) -> None:
        assert numbers_equal("50%", "0.5")

    def test_whitespace_tolerated(self) -> None:
        assert numbers_equal(" 42 ", "42")

    def test_invalid_input_returns_false(self) -> None:
        assert not numbers_equal("abc", "42")

    def test_invalid_correct_returns_false(self) -> None:
        assert not numbers_equal("42", "abc")

    def test_tiny_difference_within_tolerance(self) -> None:
        assert numbers_equal("1.0000001", "1.0")

    def test_large_difference_outside_tolerance(self) -> None:
        assert not numbers_equal("1.1", "1.0", tolerance=1e-6)


class TestIsValidNumber:
    def test_valid(self) -> None:
        assert is_valid_number("3.14")

    def test_invalid(self) -> None:
        assert not is_valid_number("not number")

    def test_empty(self) -> None:
        assert not is_valid_number("")
