"""Independent regression checks and input boundary tests for Hadlock-3."""
import math
import pytest
from biometry import estimate_fetal_weight


def test_published_hadlock_3_equation_and_units():
    # 30, 28 and 5.5 cm entered as mm.
    expected = 10 ** (1.326 - 0.00326 * 28 * 5.5 + 0.0107 * 30 + 0.0438 * 28 + 0.158 * 5.5)
    result = estimate_fetal_weight(300, 280, 55, 78)
    assert result["estimated_fetal_weight_g"] == round(expected, 1)
    assert result["measurements_mm"]["BPD"] == 78
    assert "Hadlock-3" in result["method"]


def test_bpd_not_used_in_three_parameter_equation():
    assert estimate_fetal_weight(300, 280, 55)["estimated_fetal_weight_g"] == (
        estimate_fetal_weight(300, 280, 55, 80)["estimated_fetal_weight_g"]
    )


@pytest.mark.parametrize("bad", [-2, 0, float("nan"), float("inf"), float("-inf"), 1001, "n/a", None, True])
def test_rejects_invalid_measurements(bad):
    with pytest.raises(ValueError):
        estimate_fetal_weight(bad, 280, 55)


def test_estimate_contains_no_percentile_or_diagnosis():
    result = estimate_fetal_weight(300, 280, 55)
    assert "percentile" not in result
    assert "not gestational age" in result["interpretation"].lower()
