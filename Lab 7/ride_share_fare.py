import math


def parse_trip(text):
    if not isinstance(text, str):
        raise TypeError("trip must be a string in 'cab:distance' format")

    if text.count(':') != 1:
        raise ValueError("trip must contain exactly one ':' separator")

    cab, km_text = text.split(':')
    cab = cab.strip()
    if not cab:
        raise ValueError("cab name must not be empty")

    try:
        km = float(km_text)
    except ValueError as exc:
        raise ValueError("distance must be a valid number") from exc

    if not math.isfinite(km):
        raise ValueError("distance must be finite")
    if km < 0:
        raise ValueError("distance must not be negative")

    return cab.title(), km

def fare_average(fares_csv):
    if not isinstance(fares_csv, str):
        raise TypeError("fares must be a comma-separated string")

    if not fares_csv.strip():
        raise ValueError("fares must not be empty")

    try:
        values = [int(value.strip()) for value in fares_csv.split(',')]
    except ValueError as exc:
        raise ValueError("fares must be comma-separated integers") from exc

    if any(value < 0 for value in values):
        raise ValueError("fares must not be negative")

    return sum(values) // len(values)

def payable_fare(text):
    if not isinstance(text, str):
        raise TypeError("fare and promo must be provided as a string")

    if text.count('|') != 1:
        raise ValueError("input must contain exactly one '|' separator")

    fare_text, promo_text = text.split('|')
    try:
        fare = float(fare_text)
        promo = float(promo_text)
    except ValueError as exc:
        raise ValueError("fare and promo must be valid numbers") from exc

    if not math.isfinite(fare) or not math.isfinite(promo):
        raise ValueError("fare and promo must be finite numbers")
    if fare < 0 or promo < 0:
        raise ValueError("fare and promo must not be negative")

    total = fare * 1.18 - promo
    if not math.isfinite(total):
        raise ValueError("fare and promo produce a non-finite payable amount")

    return max(total, 0)

def main():
    print("==== Running parse_trip ====")
    user_input = input("Enter cab:distance in km (e.g. sedan:12): ")
    result = parse_trip(user_input)
    print("Cab and Distance:", result)

    print("\n==== Running fare_average ====")
    user_input = input("Enter fares as CSV (e.g. 120,95,210): ")
    result = fare_average(user_input)
    print("Average Fare:", result)

    print("\n==== Running payable_fare ====")
    user_input = input("Enter fare|promo (e.g. 250|30): ")
    result = payable_fare(user_input)
    print("Payable Fare:", result)

if __name__ == "__main__":
    main()
