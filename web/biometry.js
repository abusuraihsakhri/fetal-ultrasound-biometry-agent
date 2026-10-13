/* Hadlock-3 numerical EFW. Measurements: mm -> cm; result: grams.
 * Formula: Hadlock FP et al., Am J Obstet Gynecol. 1985;151:333-337.
 * Educational demonstration; not a growth-centile or diagnostic tool.
 */
(function (root) {
  'use strict';

  function positiveMillimeters(label, value) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0 || value > 1000) {
      throw new RangeError(label + ' must be a finite, positive measurement in millimeters (max 1000).');
    }
    return value;
  }

  function estimateFetalWeight(hcMm, acMm, flMm, bpdMm = null) {
    const hc = positiveMillimeters('HC', hcMm);
    const ac = positiveMillimeters('AC', acMm);
    const fl = positiveMillimeters('FL', flMm);
    const bpd = bpdMm == null ? null : positiveMillimeters('BPD', bpdMm);
    const hcCm = hc / 10, acCm = ac / 10, flCm = fl / 10;
    const exponent = 1.326 - 0.00326 * acCm * flCm
      + 0.0107 * hcCm + 0.0438 * acCm + 0.158 * flCm;
    const grams = 10 ** exponent;
    if (!Number.isFinite(grams) || grams <= 0) {
      throw new RangeError('These inputs do not yield a valid weight estimate.');
    }
    return {
      method: 'Hadlock-3 (HC, AC, FL)',
      estimated_fetal_weight_g: Math.round((grams + Number.EPSILON) * 10) / 10,
      measurements_mm: { HC: hc, AC: ac, FL: fl, BPD: bpd },
      interpretation: 'Formula-derived estimate only. Not gestational age, percentile, growth restriction assessment, or a diagnosis.'
    };
  }

  const api = Object.freeze({ estimateFetalWeight });
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.Biometry = api;
}(typeof globalThis !== 'undefined' ? globalThis : this));
