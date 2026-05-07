"""Tests for calculator module — includes a deliberate failure."""

from calculator import add, subtract, multiply, divide, format_result, CalculatorHistory


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(10, 4) == 6


def test_multiply():
    assert multiply(3, 7) == 21


def test_divide():
    assert divide(10, 2) == 5.0


def test_divide_by_zero():
    """ISSUE: This test will FAIL — divide() doesn't handle zero."""
    try:
        divide(10, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_format_result_integer():
    assert format_result(5.0) == "5"


def test_format_result_float():
    assert format_result(3.14) == "3.14"


def test_history_add_and_get():
    history = CalculatorHistory()
    history.add_entry("add", 2, 3, 5)
    last = history.get_last()
    assert last is not None
    assert last["result"] == 5


def test_history_empty():
    history = CalculatorHistory()
    assert history.get_last() is None
    assert history.has_entries() is False
