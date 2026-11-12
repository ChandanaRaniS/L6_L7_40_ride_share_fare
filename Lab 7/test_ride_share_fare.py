import math

import pytest
from hypothesis import example, given, strategies as st
from ride_share_fare import parse_trip, fare_average, payable_fare


def _assert_fuzzed_input(function, value, is_valid, expected_result=None):
    if is_valid:
        assert function(value) == expected_result
    else:
        error = TypeError if not isinstance(value, str) else ValueError
        with pytest.raises(error, match=r".+"):
            function(value)


def _is_valid_trip(value):
    if not isinstance(value, str) or value.count(':') != 1:
        return False
    cab, distance_text = value.split(':')
    if not cab.strip():
        return False
    try:
        distance = float(distance_text)
    except ValueError:
        return False
    return math.isfinite(distance) and distance >= 0


def _is_valid_fares(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        fares = [int(item.strip()) for item in value.split(',')]
    except ValueError:
        return False
    return all(fare >= 0 for fare in fares)


def _is_valid_payable_fare(value):
    if not isinstance(value, str) or value.count('|') != 1:
        return False
    fare_text, promo_text = value.split('|')
    try:
        fare = float(fare_text)
        promo = float(promo_text)
    except ValueError:
        return False
    return (
        math.isfinite(fare)
        and math.isfinite(promo)
        and fare >= 0
        and promo >= 0
        and math.isfinite(fare * 1.18 - promo)
    )


# Try arbitrary strings, unexpected types, and trip-shaped strings with
# generated numeric distances (including negative, zero, and large values).
@given(
    st.one_of(
        st.text(),
        st.none(),
        st.integers(),
        st.floats(),
        st.booleans(),
        st.lists(st.integers()),
        st.tuples(st.text(), st.floats()).map(
            lambda parts: f"{parts[0]}:{parts[1]}"
        ),
    )
)
@example(s=None)
@example(s="")
@example(s="sedan:0")
@example(s="sedan")
@example(s="sedan:12:3")
@example(s="sedan:invalid")
@example(s="sedan:-1")
def test_parse_trip_validates_fuzzed_input(s):
    is_valid = _is_valid_trip(s)
    expected = None
    if is_valid:
        cab, distance = s.split(':')
        expected = cab.strip().title(), float(distance)
    _assert_fuzzed_input(parse_trip, s, is_valid, expected)


# CSV-shaped fare lists include empty lists, negative values, zero, and
# arbitrarily large integers; other branches try malformed strings and types.
@given(
    st.one_of(
        st.text(),
        st.none(),
        st.integers(),
        st.floats(),
        st.booleans(),
        st.lists(st.integers()).map(
            lambda fares: ",".join(str(fare) for fare in fares)
        ),
        st.lists(st.text()),
    )
)
@example(s=None)
@example(s="")
@example(s="0,0")
@example(s="1,,2")
@example(s="invalid,2")
@example(s="-1,2")
def test_fare_average_validates_fuzzed_input(s):
    is_valid = _is_valid_fares(s)
    expected = None
    if is_valid:
        values = [int(item.strip()) for item in s.split(',')]
        expected = sum(values) // len(values)
    _assert_fuzzed_input(fare_average, s, is_valid, expected)


# Try arbitrary inputs and fare|promo strings with generated numeric values.
@given(
    st.one_of(
        st.text(),
        st.none(),
        st.integers(),
        st.floats(),
        st.booleans(),
        st.tuples(st.floats(), st.floats()).map(
            lambda values: f"{values[0]}|{values[1]}"
        ),
    )
)
@example(s=None)
@example(s="")
@example(s="0|0")
@example(s="250|500")
@example(s="250")
@example(s="250|30|5")
@example(s="invalid|30")
@example(s="-1|0")
@example(s="250|-30")
def test_payable_fare_validates_fuzzed_input(s):
    is_valid = _is_valid_payable_fare(s)
    expected = None
    if is_valid:
        fare_text, promo_text = s.split('|')
        expected = max(float(fare_text) * 1.18 - float(promo_text), 0)
    _assert_fuzzed_input(payable_fare, s, is_valid, expected)


def test_valid_inputs_keep_their_existing_results():
    assert parse_trip("sedan:12") == ("Sedan", 12.0)
    assert fare_average("120,95,210") == 141
    assert payable_fare("250|30") == 265
