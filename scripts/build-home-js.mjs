#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { minify } from 'terser';

const root = path.resolve(import.meta.dirname, '..');
const sources = [
  'assets/js/icons.js',
  'assets/js/product-image-utils.js',
  'assets/js/site.js',
  'assets/js/CompareManager.js',
  'assets/js/Header.js',
  'assets/js/MegaMenu.js',
  'assets/js/main.js',
  'assets/js/pages/home.js',
];
const outputPath = path.join(root, 'assets/js/home.bundle.min.js');
const indexPath = path.join(root, 'index.html');

const source = (
  await Promise.all(
    sources.map(async (relative) => {
      const code = await readFile(path.join(root, relative), 'utf8');
      return `\n/* ${relative} */\n${code}\n`;
    }),
  )
).join('');
const result = await minify(source, {
  compress: { passes: 2 },
  mangle: true,
  format: { comments: false },
});
if (!result.code) throw new Error('Homepage JavaScript bundle üretilemedi.');
await writeFile(outputPath, `${result.code}\n`, 'utf8');

const hash = createHash('md5').update(result.code).digest('hex').slice(0, 8);
const html = await readFile(indexPath, 'utf8');
const scriptBlock =
  /[ \t]*<script defer src="assets\/js\/icons\.js\?v=[^"]+"><\/script>[\s\S]*?<script defer src="assets\/js\/pages\/home\.js\?v=[^"]+"><\/script>/;
if (!scriptBlock.test(html)) throw new Error('index.html ana sayfa script bloğu bulunamadı.');
await writeFile(
  indexPath,
  html.replace(
    scriptBlock,
    `  <script defer src="assets/js/home.bundle.min.js?v=${hash}"></script>`,
  ),
  'utf8',
);
console.log(`home.bundle.min.js ?v=${hash} (${(result.code.length / 1024).toFixed(1)} KB)`);
