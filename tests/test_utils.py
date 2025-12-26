from utils import chunks, unique, isiterable, format_dict


def test_unique() -> None:
    lst = [1, 2, 2, 3, 4, 4, 5]
    assert unique(lst) == [1, 2, 3, 4, 5]


def test_unique_empty_list() -> None:
    assert unique([]) == []


def test_unique_preserves_order() -> None:
    lst = [3, 1, 2, 1, 3, 4]
    assert unique(lst) == [3, 1, 2, 4]


def test_chunks() -> None:
    lst = [1, 2, 3, 4, 5, 6]
    assert list(chunks(lst, 2)) == [[1, 2], [3, 4], [5, 6]]
    assert list(chunks(lst, 3)) == [[1, 2, 3], [4, 5, 6]]
    assert list(chunks(lst, 4)) == [[1, 2, 3, 4], [5, 6]]
    assert list(chunks(lst, 5)) == [[1, 2, 3, 4, 5], [6]]
    assert list(chunks(lst, 6)) == [[1, 2, 3, 4, 5, 6]]
    assert list(chunks(lst, 7)) == [[1, 2, 3, 4, 5, 6]]


def test_chunks_empty_list() -> None:
    assert list(chunks([], 3)) == []


def test_isiterable_with_iterable_types() -> None:
    """Test that isiterable returns True for iterable types."""
    assert isiterable([1, 2, 3]) is True
    assert isiterable((1, 2, 3)) is True
    assert isiterable({1, 2, 3}) is True
    assert isiterable("string") is True
    assert isiterable({"key": "value"}) is True
    assert isiterable(range(5)) is True


def test_isiterable_with_non_iterable_types() -> None:
    """Test that isiterable returns False for non-iterable types."""
    assert isiterable(42) is False
    assert isiterable(3.14) is False
    assert isiterable(True) is False
    assert isiterable(None) is False


def test_format_dict_simple() -> None:
    """Test format_dict with a simple dictionary."""
    obj_dict = {"name": "Alice", "age": 30}
    result = format_dict(obj_dict)
    assert "- name" in result
    assert "- age" in result


def test_format_dict_nested() -> None:
    """Test format_dict with nested dictionaries."""
    obj_dict = {
        "user": {
            "name": "Alice",
            "address": {
                "city": "Moscow",
                "country": "Russia"
            }
        }
    }
    result = format_dict(obj_dict)

    # Check that all keys are present
    assert "- user" in result
    assert "- name" in result
    assert "- address" in result
    assert "- city" in result
    assert "- country" in result

    # Check indentation (nested items should have more spaces)
    lines = result.split("\n")
    # First level should have no indentation
    assert any(line.startswith("- user") for line in lines)
    # Second level should have 2 spaces
    assert any(line.startswith("  - name") for line in lines)
    # Third level should have 4 spaces
    assert any(line.startswith("    - city") for line in lines)


def test_format_dict_empty() -> None:
    """Test format_dict with an empty dictionary."""
    assert format_dict({}) == ""


def test_format_dict_with_indent() -> None:
    """Test format_dict with custom indent level."""
    obj_dict = {"key": "value"}
    result = format_dict(obj_dict, indent=2)
    assert result.startswith("    - key")  # 2 * 2 spaces
