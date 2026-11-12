import pytest

from ride_share_fare import extra_distance_fare, pickup_status, seats_and_bags_ok


def test_extra_distance_fare_rejects_unknown_cabs_and_negative_distance():
    with pytest.raises(ValueError, match="unknown cab type"):
        extra_distance_fare("van", 10, "city", False)

    with pytest.raises(ValueError, match="invalid distance"):
        extra_distance_fare("mini", -1, "city", False)


@pytest.mark.parametrize(
    "cab_type, distance, zone, subscriber, expected",
    [
        ("mini", 5, "city", False, 0),       # At the included-distance limit
        ("mini", 4, "city", False, 0),       # Below the included-distance limit
        ("mini", 6, "city", False, 12),      # One extra city kilometre
        ("sedan", 10, "city", False, 24),    # Two extra city kilometres
        ("sedan", 12, "city", True, 12),     # Subscriber gets 3 more included km
        ("suv", 13, "city", True, 12),       # SUV does not get subscriber km
        ("mini", 6, "outstation", False, 18),
        ("mini", 25, "city", False, 240),    # Exactly 20 extra km: no surcharge
        ("mini", 26, "city", False, 420),    # 21 extra km: city surcharge applies
        ("mini", 26, "outstation", False, 630),  # Outstation surcharge also applies
    ],
)
def test_extra_distance_fare_calculations(
    cab_type, distance, zone, subscriber, expected
):
    assert extra_distance_fare(cab_type, distance, zone, subscriber) == expected


@pytest.mark.parametrize(
    "passengers, bags, wheelchair, expected",
    [
        (2, 100, True, True),  # Wheelchair rides only check the passenger limit
        (3, 0, True, False),   # More than 2 passengers with a wheelchair
        (4, 2, False, True),   # Passenger and bag limits are inclusive
        (5, 0, False, False),  # More than 4 passengers
        (4, 3, False, False),  # More than 2 bags
    ],
)
def test_seats_and_bags_limits(passengers, bags, wheelchair, expected):
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
def test_pickup_status_boundaries(scheduled, airport, cutoff):
    # The cutoff itself is on time; the next 15 minutes are delayed.
    assert pickup_status(cutoff, scheduled, airport) == "on_time"
    assert pickup_status(cutoff - 1, scheduled, airport) == "delayed"
    assert pickup_status(cutoff - 15, scheduled, airport) == "delayed"
    assert pickup_status(cutoff - 16, scheduled, airport) == "missed"
