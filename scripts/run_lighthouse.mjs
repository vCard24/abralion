import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const url = process.argv[2] || 'https://abralion.com/';
const strategies = process.argv.slice(3);
const toRun = strategies.length ? strategies : ['desktop', 'mobile'];

async function run(strategy) {
  const chrome = await chromeLauncher.launch({
    chromeFlags: ['--headless', '--no-sandbox', '--disable-gpu'],
  });
  try {
    const result = await lighthouse(url, {
      logLevel: 'error',
      output: 'json',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      port: chrome.port,
      formFactor: strategy,
      screenEmulation: { mobile: strategy === 'mobile' },
    });
    const lhr = result.lhr;
    const c = lhr.categories;
    const a = lhr.audits;
    const summary = {
      strategy,
      url,
      fetched: lhr.fetchTime,
      scores: {
        performance: Math.round((c.performance?.score || 0) * 100),
        accessibility: Math.round((c.accessibility?.score || 0) * 100),
        bestPractices: Math.round((c['best-practices']?.score || 0) * 100),
        seo: Math.round((c.seo?.score || 0) * 100),
      },
      metrics: {
        fcp: a['first-contentful-paint']?.displayValue,
        lcp: a['largest-contentful-paint']?.displayValue,
        tbt: a['total-blocking-time']?.displayValue,
        cls: a['cumulative-layout-shift']?.displayValue,
        si: a['speed-index']?.displayValue,
      },
      clsShifts: (a['layout-shifts']?.details?.items || [])
        .slice(0, 10)
        .map((i) => ({ score: i.score, snippet: i.node?.snippet })),
      contrastFails: (a['color-contrast']?.details?.items || [])
        .slice(0, 10)
        .map((i) => ({
          snippet: i.node?.snippet,
          explanation: i.node?.explanation,
        })),
      consoleErrors: a['errors-in-console']?.details?.items?.length || 0,
    };
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    const file = path.join(root, `lighthouse-${strategy}-${stamp}.json`);
    fs.writeFileSync(file, JSON.stringify(summary, null, 2));
    console.log(JSON.stringify(summary, null, 2));
    return summary;
  } finally {
    await chrome.kill();
  }
}

for (const strategy of toRun) {
  console.log(`\n=== Lighthouse ${strategy} ===`);
  await run(strategy);
}
