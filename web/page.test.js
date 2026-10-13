'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const Biometry = require('./biometry.js');

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const controller = html.match(/<script>([\s\S]*?)<\/script>/);

test('page loads its local calculator and contains valid inline JavaScript', () => {
  assert.match(html, /<script src="\.\/biometry\.js"><\/script>/);
  assert.ok(controller, 'Inline form controller exists');
  assert.doesNotThrow(() => new vm.Script(controller[1], {filename: 'web/index.html'}));
  assert.doesNotMatch(controller[1], /\bfetch\s*\(/);
});

test('form submits, renders estimate, rejects invalid fields and enables CSV export', () => {
  const elements = new Map();
  const el = id => {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', hidden: true, disabled: true, listeners: {},
      addEventListener(type, callback) { this.listeners[type] = callback; },
    });
    return elements.get(id);
  };
  el('hc').value = '300'; el('ac').value = '280'; el('fl').value = '55'; el('bpd').value = '78';
  const links = [];
  let createdBlob;
  const sandbox = {
    document: {
      getElementById: el,
      createElement() {
        const link = { href: '', download: '', clicked: false,
          click() { this.clicked = true; },
          remove() {} };
        links.push(link);
        return link;
      },
      body: { append() {} }
    },
    Biometry,
    URL: {createObjectURL(blob) { createdBlob = blob; return 'blob:csv'; }, revokeObjectURL() {}},
    Blob,
    setTimeout(callback) { callback(); }
  };
  vm.runInNewContext(controller[1], sandbox);
  const form = el('biometry-form');
  form.listeners.submit({preventDefault() {}});
  assert.match(el('efw-value').textContent, /g$/);
  assert.equal(el('download').disabled, false);
  assert.equal(el('out-bpd').textContent, '78 mm');
  el('download').listeners.click();
  assert.ok(createdBlob);
  assert.equal(links[0].download, 'fetal-biometry-efw.csv');
  assert.equal(links[0].clicked, true);

  el('hc').value = '-2';
  form.listeners.input();
  form.listeners.submit({preventDefault() {}});
  assert.equal(el('validation-error').hidden, false);
  assert.match(el('validation-error').textContent, /HC/);
  assert.equal(el('download').disabled, true);
});
