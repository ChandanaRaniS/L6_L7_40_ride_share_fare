import pytest

from ride_share_fare import extra_distance_fare, pickup_status, seats_and_bags_ok


def test_extra_distance_fare_exception_branches():
    with pytest.raises(ValueError, match="unknown cab type"):
        extra_distance_fare("van", 10, "city", False)

    with pytest.raises(ValueError, match="invalid distance"):
        extra_distance_fare("mini", -1, "city", False)


@pytest.mark.parametrize(
    "cab_type, distance, zone, subscriber, expected",
    [
        ("mini", 5, "city", False, 0),          # No extra distance
        ("mini", 9, "city", True, 12),          # Subscriber inclusion applies
        ("suv", 13, "city", True, 12),          # Subscriber inclusion skips SUV
        ("mini", 6, "outstation", False, 18),   # Non-city rate without surcharge
        ("mini", 26, "city", False, 420),       # City rate with surcharge
        ("mini", 26, "outstation", False, 630), # Outstation rate and surcharge
    ],
)
def test_extra_distance_fare_decision_branches(
    cab_type, distance, zone, subscriber, expected
):
    assert extra_distance_fare(cab_type, distance, zone, subscriber) == expected


@pytest.mark.parametrize(
    "passengers, bags, wheelchair, expected",
    [
        (2, 3, True, True),    # Wheelchair passenger limit accepts 2
        (3, 0, True, False),   # Wheelchair passenger limit rejects 3
        (5, 0, False, False),  # Regular passenger limit rejects 5
        (4, 2, False, True),   # Regular passenger and bag limits accept limits
        (4, 3, False, False),  # Regular bag limit rejects 3
    ],
)
def test_seats_and_bags_decision_branches(passengers, bags, wheelchair, expected):
    assert seats_and_bags_ok(passengers, bags, wheelchair) is expected


@pytest.mark.parametrize(
    "scheduled, airport, cutoff",
    [
        (False, False, 5),
        (False, True, 15),
        (True, False, 10),
        (True, True, 20),
    ],
)
def test_pickup_status_decision_branches(scheduled, airport, cutoff):
    assert pickup_status(cutoff, scheduled, airport) == "on_time"
    assert pickup_status(cutoff - 1, scheduled, airport) == "delayed"
    assert pickup_status(cutoff - 15, scheduled, airport) == "delayed"
    assert pickup_status(cutoff - 16, scheduled, airport) == "missed"
