/**
 * Compare hero layout before/after async bundle.min.css applies.
 * Usage: node scripts/verify_hero_cls.mjs
 */
import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fileUrl = `file://${path.join(root, 'index.html').replace(/\\/g, '/')}`;

async function waitForHeroFonts(page, width) {
  const titleSize = width >= 1024 ? '64px' : '32px';
  await page.waitForFunction(
    (size) => document.fonts.check(`700 ${size} Montserrat`),
    titleSize
  );
  await page.waitForFunction(() => document.fonts.check('400 18px Inter'));
}

async function snapshot(page) {
  return page.evaluate(() => {
    const hero = document.getElementById('home-hero');
    const main = document.getElementById('main-content');
    const title = hero?.querySelector('.home-hero__title');
    const subtitle = hero?.querySelector('.home-hero__subtitle');
    const stats = hero?.querySelector('.home-hero__stats');
    const box = (el) => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return {
        h: Math.round(r.height * 10) / 10,
        w: Math.round(r.width * 10) / 10,
        fs: cs.fontSize,
        lh: cs.lineHeight,
        mt: cs.marginTop,
        mb: cs.marginBottom,
        pt: cs.paddingTop,
        pb: cs.paddingBottom,
      };
    };
    return {
      heroH: hero ? Math.round(hero.getBoundingClientRect().height * 10) / 10 : null,
      mainH: main ? Math.round(main.getBoundingClientRect().height * 10) / 10 : null,
      title: box(title),
      subtitle: box(subtitle),
      stats: box(stats),
      bundleOn:
        [...document.querySelectorAll('link[rel="stylesheet"]')].some(
          (l) => l.href.includes('bundle.min.css') && l.media === 'all'
        ),
    };
  });
}

async function runViewport(browser, width, height) {
  const page = await browser.newPage({ viewport: { width, height } });
  await page.addInitScript(() => {
    document.addEventListener(
      'DOMContentLoaded',
      () => {
        const bundle = document.querySelector('link[href*="bundle.min.css"]');
        if (bundle) {
          bundle.removeAttribute('onload');
          bundle.media = 'not all';
        }
        const fonts = document.querySelector('link[href*="fonts.googleapis.com"]');
        if (fonts) {
          fonts.removeAttribute('onload');
          fonts.media = 'all';
        }
      },
      { once: true }
    );
  });
  await page.goto(fileUrl, { waitUntil: 'domcontentloaded' });
  await waitForHeroFonts(page, width);
  await page.waitForTimeout(50);
  const criticalOnly = await snapshot(page);
  await page.evaluate(() => {
    const link = document.querySelector('link[href*="bundle.min.css"]');
    if (link) link.media = 'all';
  });
  await page.waitForFunction(() => {
    const link = [...document.querySelectorAll('link[rel="stylesheet"]')].find((l) =>
      l.href.includes('bundle.min.css')
    );
    return link && link.media === 'all';
  });
  await waitForHeroFonts(page, width);
  await page.waitForTimeout(100);
  const withBundle = await snapshot(page);
  await page.close();
  return { width, criticalOnly, withBundle };
}

function diff(a, b) {
  const keys = new Set([...Object.keys(a || {}), ...Object.keys(b || {})]);
  const out = {};
  for (const k of keys) {
    const av = a?.[k];
    const bv = b?.[k];
    if (typeof av === 'object' && av && typeof bv === 'object' && bv) {
      const nested = diff(av, bv);
      if (Object.keys(nested).length) out[k] = nested;
    } else if (av !== bv) {
      out[k] = { before: av, after: bv };
    }
  }
  return out;
}

function heroLayoutDelta(before, after) {
  const delta = diff(before, after);
  delete delta.bundleOn;
  delete delta.mainH;
  return delta;
}

const browser = await chromium.launch();
const results = [];
for (const vp of [
  { width: 375, height: 812 },
  { width: 1280, height: 800 },
]) {
  results.push(await runViewport(browser, vp.width, vp.height));
}
await browser.close();

let failed = false;
for (const r of results) {
  const delta = heroLayoutDelta(r.criticalOnly, r.withBundle);
  console.log(`\n=== ${r.width}px ===`);
  console.log('critical-only', JSON.stringify(r.criticalOnly, null, 2));
  console.log('with-bundle ', JSON.stringify(r.withBundle, null, 2));
  if (Object.keys(delta).length) {
    failed = true;
    console.log('DELTA', JSON.stringify(delta, null, 2));
  } else {
    console.log('OK: no layout delta after bundle');
  }
}
process.exit(failed ? 1 : 0);
