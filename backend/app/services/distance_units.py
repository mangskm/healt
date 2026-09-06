from decimal import Decimal, ROUND_HALF_UP

from app.models.exercise import DistanceUnit

KM_PER_MILE = Decimal("1.609344")
DISTANCE_STORAGE_PRECISION = Decimal("0.001")


def to_kilometers(distance: Decimal, unit: DistanceUnit) -> Decimal:
    kilometers = distance if unit is DistanceUnit.KILOMETERS else distance * KM_PER_MILE
    return kilometers.quantize(DISTANCE_STORAGE_PRECISION, rounding=ROUND_HALF_UP)
