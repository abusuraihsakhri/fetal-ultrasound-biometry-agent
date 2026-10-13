"""Educational Hadlock-3 fetal weight calculation from *measured* HC, AC, FL.

Hadlock FP et al. AJOG 1985;151:333-337. Inputs are mm, transformed to
cm for the published log10(EFW in grams) regression. Do not infer fetal
growth restriction, centiles, or gestational dating from this function.
"""
import math
from typing import Dict, Optional


def _millimeters(name: str, value: float) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite positive measurement in mm")
    try:
        measurement = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite positive measurement in mm") from exc
    if not math.isfinite(measurement) or not (0 < measurement <= 1000):
        raise ValueError(f"{name} must be a finite positive measurement in mm (max 1000)")
    return measurement


def estimate_fetal_weight(
    hc_mm: float, ac_mm: float, fl_mm: float, bpd_mm: Optional[float] = None
) -> Dict[str, object]:
    """Compute Hadlock-3 EFW from HC/AC/FL, with optional recorded BPD.

    Returns estimated weight (grams) and units/formula metadata. BPD is
    included for transparency but is *not used* in the Hadlock-3 equation.
    Inputs require qualified sonographic acquisition and interpretation.
    """
    hc = _millimeters("HC", hc_mm)
    ac = _millimeters("AC", ac_mm)
    fl = _millimeters("FL", fl_mm)
    bpd = _millimeters("BPD", bpd_mm) if bpd_mm is not None else None
    hc_cm, ac_cm, fl_cm = hc / 10.0, ac / 10.0, fl / 10.0
    log10_efw = (
        1.326
        - 0.00326 * ac_cm * fl_cm
        + 0.0107 * hc_cm
        + 0.0438 * ac_cm
        + 0.158 * fl_cm
    )
    efw = 10 ** log10_efw
    if not math.isfinite(efw) or efw <= 0:
        raise ValueError("Measurements produce an invalid estimated weight")
    return {
        "method": "Hadlock-3 (HC, AC, FL)",
        "estimated_fetal_weight_g": round(efw, 1),
        "measurements_mm": {"HC": hc, "AC": ac, "FL": fl, "BPD": bpd},
        "interpretation": (
            "Formula-derived estimate only. Not gestational age, percentile, "
            "growth restriction assessment, or a diagnosis."
        ),
    }
