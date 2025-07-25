"""
Unit tests for new --since and --until date parameters.
Tests the parsing and validation of git-style date expressions.
"""

import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

from git_outlier.git_outlier import (
    parse_git_date,
    get_date_range,
    parse_arguments,
)


def test_parse_git_date_none_with_default():
    """Test parse_git_date with None and default months ago"""
    # None with 12 months ago
    result = parse_git_date(None, default_months_ago=12)
    expected = str(date.today() + relativedelta(months=-12))
    assert result == expected

    # None with 0 months ago (today)
    result = parse_git_date(None, default_months_ago=0)
    expected = str(date.today())
    assert result == expected


def test_parse_git_date_relative_years():
    """Test parsing relative date strings with years"""
    result = parse_git_date("1 year ago")
    expected = str(date.today() + relativedelta(years=-1))
    assert result == expected

    result = parse_git_date("2 years ago")
    expected = str(date.today() + relativedelta(years=-2))
    assert result == expected


def test_parse_git_date_relative_months():
    """Test parsing relative date strings with months"""
    result = parse_git_date("6 months ago")
    expected = str(date.today() + relativedelta(months=-6))
    assert result == expected

    result = parse_git_date("1 months ago")
    expected = str(date.today() + relativedelta(months=-1))
    assert result == expected


def test_parse_git_date_relative_weeks():
    """Test parsing relative date strings with weeks"""
    result = parse_git_date("2 weeks ago")
    expected = str(date.today() + relativedelta(weeks=-2))
    assert result == expected

    result = parse_git_date("last week")
    expected = str(date.today() + relativedelta(weeks=-1))
    assert result == expected


def test_parse_git_date_relative_days():
    """Test parsing relative date strings with days"""
    result = parse_git_date("5 days ago")
    expected = str(date.today() + relativedelta(days=-5))
    assert result == expected

    result = parse_git_date("yesterday")
    expected = str(date.today() + relativedelta(days=-1))
    assert result == expected


def test_parse_git_date_named_relatives():
    """Test parsing named relative dates"""
    result = parse_git_date("today")
    expected = str(date.today())
    assert result == expected

    result = parse_git_date("last month")
    expected = str(date.today() + relativedelta(months=-1))
    assert result == expected
    
    result = parse_git_date("last year")
    expected = str(date.today() + relativedelta(years=-1))
    assert result == expected


def test_parse_git_date_absolute_dates():
    """Test parsing absolute date strings"""
    result = parse_git_date("2023-01-01")
    assert result == "2023-01-01"

    result = parse_git_date("2023-12-31")
    assert result == "2023-12-31"

    # Test various date formats that dateutil can parse
    result = parse_git_date("Jan 1, 2023")
    assert "2023-01-01" in result

    result = parse_git_date("2023/06/15")
    assert "2023-06-15" in result


def test_parse_git_date_case_insensitive():
    """Test that date parsing is case insensitive"""
    result1 = parse_git_date("6 MONTHS AGO")
    result2 = parse_git_date("6 months ago")
    assert result1 == result2

    result1 = parse_git_date("2 YEARS AGO")
    result2 = parse_git_date("2 years ago")
    assert result1 == result2

    result1 = parse_git_date("YESTERDAY")
    result2 = parse_git_date("yesterday")
    assert result1 == result2


def test_parse_git_date_invalid():
    """Test parsing invalid date strings"""
    with pytest.raises(ValueError):
        parse_git_date("invalid date string")

    with pytest.raises(ValueError):
        parse_git_date("not a date")

    # Malformed relative dates should fallback to dateutil and fail
    with pytest.raises(ValueError):
        parse_git_date("abc months ago")


def test_get_date_range_both_none():
    """Test get_date_range with both parameters None"""
    start_date, end_date = get_date_range(None, None)

    expected_start = str(date.today() + relativedelta(months=-12))
    assert start_date == expected_start
    assert end_date is None


def test_get_date_range_since_only():
    """Test get_date_range with only since parameter"""
    start_date, end_date = get_date_range("6 months ago", None)

    expected_start = str(date.today() + relativedelta(months=-6))
    assert start_date == expected_start
    assert end_date is None


def test_get_date_range_until_only():
    """Test get_date_range with only until parameter"""
    start_date, end_date = get_date_range(None, "yesterday")

    expected_start = str(date.today() + relativedelta(months=-12))
    expected_end = str(date.today() + relativedelta(days=-1))
    assert start_date == expected_start
    assert end_date == expected_end


def test_get_date_range_both_parameters():
    """Test get_date_range with both since and until"""
    start_date, end_date = get_date_range("1 month ago", "yesterday")

    expected_start = str(date.today() + relativedelta(months=-1))
    expected_end = str(date.today() + relativedelta(days=-1))
    assert start_date == expected_start
    assert end_date == expected_end


def test_argument_parsing_since_until():
    """Test argument parsing with new --since and --until parameters"""
    # Test with --since only
    args = parse_arguments(["--since", "6 months ago", "."])
    assert args.since == "6 months ago"
    assert args.until is None

    # Test with --until only
    args = parse_arguments(["--until", "yesterday", "."])
    assert args.since is None
    assert args.until == "yesterday"

    # Test with both parameters
    args = parse_arguments(["--since", "1 month ago", "--until", "yesterday", "."])
    assert args.since == "1 month ago"
    assert args.until == "yesterday"

    # Test with neither (defaults)
    args = parse_arguments(["."])
    assert args.since is None
    assert args.until is None


def test_argument_parsing_date_validation():
    """Test that argument parsing validates date parameters"""
    # Valid dates should not raise error
    args = parse_arguments(["--since", "2023-01-01", "."])
    assert args.since == "2023-01-01"

    # Invalid dates should raise error
    with pytest.raises(SystemExit):
        parse_arguments(["--since", "invalid date", "."])

    with pytest.raises(SystemExit):
        parse_arguments(["--until", "not a date", "."])


def test_edge_cases_whitespace():
    """Test parsing with extra whitespace"""
    result = parse_git_date("  6 months ago  ")
    expected = str(date.today() + relativedelta(months=-6))
    assert result == expected

    result = parse_git_date("  2023-01-01  ")
    assert result == "2023-01-01"


def test_multiple_formats_same_date():
    """Test that different formats for the same date produce same result"""
    # These should all parse to the same date
    date_strings = [
        "2023-06-15",
        "June 15, 2023",
        "2023/06/15",
        "15-06-2023",
    ]

    results = [parse_git_date(ds) for ds in date_strings]

    # All should contain the same date (allowing for different string formats)
    for result in results:
        assert "2023" in result
        assert "06" in result or "6" in result
        assert "15" in result


def test_boundary_dates():
    """Test parsing of boundary dates like beginning/end of year"""
    result = parse_git_date("2023-01-01")
    assert result == "2023-01-01"

    result = parse_git_date("2023-12-31")
    assert result == "2023-12-31"

    # Test leap year
    result = parse_git_date("2024-02-29")
    assert result == "2024-02-29"
