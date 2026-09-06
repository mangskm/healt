from decimal import Decimal, ROUND_HALF_UP

from app.models.profile import WeightUnit

KG_PER_POUND = Decimal("0.45359237")
STORAGE_PRECISION = Decimal("0.001")


def to_kilograms(weight: Decimal, unit: WeightUnit) -> Decimal:
    kilograms = weight if unit is WeightUnit.KILOGRAMS else weight * KG_PER_POUND
    return kilograms.quantize(STORAGE_PRECISION, rounding=ROUND_HALF_UP)
