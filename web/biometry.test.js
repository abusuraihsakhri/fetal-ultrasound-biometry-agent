'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { estimateFetalWeight } = require('./biometry.js');

test('Hadlock-3 reference equation uses cm internally and returns grams', () => {
  const expected = 10 ** (1.326 - 0.00326 * 28 * 5.5 + 0.0107 * 30 + 0.0438 * 28 + 0.158 * 5.5);
  const actual = estimateFetalWeight(300, 280, 55, 78);
  assert.ok(Math.abs(actual.estimated_fetal_weight_g - expected) < 0.051);
  assert.equal(actual.measurements_mm.BPD, 78);
  assert.match(actual.method, /Hadlock-3/);
});

test('BPD does not affect the three-parameter estimate', () => {
  assert.equal(estimateFetalWeight(300, 280, 55).estimated_fetal_weight_g,
    estimateFetalWeight(300, 280, 55, 90).estimated_fetal_weight_g);
});

test('rejects nonfinite, missing, zero, negative, or unreasonable values', () => {
  for (const bad of [null, undefined, NaN, Infinity, -Infinity, 0, -1, 1001, '300', true]) {
    assert.throws(() => estimateFetalWeight(bad, 280, 55), RangeError);
  }
  assert.throws(() => estimateFetalWeight(300, 280, 55, 0), RangeError);
});

test('result does not create a growth percentile or medical diagnosis', () => {
  const result = estimateFetalWeight(300, 280, 55);
  assert.ok(!('percentile' in result));
  assert.match(result.interpretation, /not gestational age/i);
});
