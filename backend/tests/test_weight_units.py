from decimal import Decimal

from app.models.profile import WeightUnit
from app.services.weight_units import to_kilograms


def test_converts_pounds_to_canonical_kilograms() -> None:
    assert to_kilograms(Decimal("150"), WeightUnit.POUNDS) == Decimal("68.039")


def test_preserves_kilograms_at_storage_precision() -> None:
    assert to_kilograms(Decimal("68.0394"), WeightUnit.KILOGRAMS) == Decimal("68.039")
