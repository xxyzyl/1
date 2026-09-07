const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const file = '/workspace/life-decision-design.html';
const html = fs.readFileSync(file, 'utf8');
assert(!html.includes(String.fromCharCode(92) + '"'));
assert(!html.includes(String.fromCharCode(92) + 'n'));
assert(!/<!doctype|<html\b|<head\b|<body\b/i.test(html));
assert(Buffer.byteLength(html) < 1000000);
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
assert.strictEqual(new Set(ids).size, ids.length);
const sourceModules = JSON.parse(fs.readFileSync('/root/.codex/skills/remote-skills/scientific-life-decisions/references/模块清单.json', 'utf8'));
const buttons = [...html.matchAll(/<button\b([^>]+)>/g)].map(m => {
  const attrs = Object.fromEntries([...m[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(a => [a[1], a[2]]));
  return {
    attrs, dataset: {module: attrs['data-module']}, events: {},
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    addEventListener(k, fn) { this.events[k] = fn; }
  };
});
assert.deepStrictEqual(buttons.map(b => b.dataset.module).sort(), sourceModules.map(m => m.id).sort());
const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(source);
for (const width of [320, 736]) {
  const nodes = Object.fromEntries(ids.map(id => [id, {
    attrs: {}, textContent: '', children: [],
    setAttribute(k, v) { this.attrs[k] = v; },
    append(v) { this.children.push(v); },
    replaceChildren() { this.children = []; }
  }]));
  const stages = ['input', 'coordinator', 'modules', 'review', 'choice', 'feedback'];
  const root = nodes['life-decision-design'];
  root.getBoundingClientRect = () => ({top: 0, width, height: 900});
  stages.forEach((name, i) => nodes['ld-' + name].getBoundingClientRect = () => ({top: i * 130 + 10, bottom: i * 130 + 60}));
  root.querySelectorAll = selector => {assert.strictEqual(selector, '[data-module]'); return buttons;};
  root.querySelector = selector => {const node = nodes[selector.slice(1)]; assert(node, selector); return node;};
  const context = {
    document: {
      getElementById(id) {assert(nodes[id]); return nodes[id];},
      createElementNS(ns, tag) {
        assert.strictEqual(ns, 'http://www.w3.org/2000/svg');
        return {tag, attrs: {}, textContent: '', setAttribute(k, v) {this.attrs[k] = v;}};
      }
    },
    ResizeObserver: class {constructor(cb) {this.cb = cb;} observe(node) {assert.strictEqual(node, root); this.cb();}},
    requestAnimationFrame: cb => cb()
  };
  vm.runInNewContext(source, context);
  const paths = nodes['ld-paths'].children.filter(node => node.tag === 'path');
  assert.strictEqual(paths.length, 8);
  paths.forEach(path => assert(!/NaN|undefined/.test(path.attrs.d)));
  for (const button of buttons) {
    button.events.click();
    assert(nodes['ld-detail'].textContent.includes(button.dataset.module));
    assert(nodes['ld-detail'].textContent.includes(' → '));
    assert(!nodes['ld-detail'].textContent.includes('undefined'));
    assert.strictEqual(buttons.filter(b => b.attrs['aria-pressed'] === 'true').length, 1);
  }
  console.log(JSON.stringify({width, modules: buttons.length, selectedStates: 23, flowPaths: paths.length, result: 'pass', scope: 'DOM simulation; not browser layout verification'}));
}
