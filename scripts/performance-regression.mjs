#!/usr/bin/env node
import { access, readFile } from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import process from 'node:process';
import { gzipSync } from 'node:zlib';
import puppeteer from 'puppeteer-core';

const ROOT = path.resolve(import.meta.dirname, '..');
const PORT = Number(process.env.PERF_PORT || 4173);
const RUNS = Number(process.env.PERF_RUNS || 3);
const CSS_DELAY_MS = Number(process.env.PERF_CSS_DELAY_MS || 1500);
const REPORT_ONLY = process.argv.includes('--report-only');
const BASE_URL = process.env.PERF_URL || `http://127.0.0.1:${PORT}/`;
const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
].filter(Boolean);

const PROFILES = {
  mobile: {
    viewport: { width: 390, height: 844, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
    userAgent:
      'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 Chrome/126 Mobile Safari/537.36',
  },
  desktop: {
    viewport: { width: 1365, height: 768, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36',
  },
  'mobile-css-delay': {
    viewport: { width: 390, height: 844, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
    userAgent:
      'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 Chrome/126 Mobile Safari/537.36',
    stability: true,
  },
  'desktop-css-delay': {
    viewport: { width: 1365, height: 768, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36',
    stability: true,
  },
};

async function chromePath() {
  for (const candidate of CHROME_CANDIDATES) {
    try {
      await access(candidate);
      return candidate;
    } catch {
      // Try next installed browser.
    }
  }
  throw new Error('Chrome/Edge bulunamadı. CHROME_PATH ortam değişkenini ayarlayın.');
}

async function startServer() {
  if (process.env.PERF_URL) return null;
  const types = {
    '.avif': 'image/avif',
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp',
    '.woff2': 'font/woff2',
  };
  const server = http.createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url, BASE_URL).pathname);
      const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
      const file = path.resolve(ROOT, relative);
      if (!file.startsWith(`${ROOT}${path.sep}`) && file !== path.join(ROOT, 'index.html')) {
        response.writeHead(403).end();
        return;
      }
      let body = await readFile(file);
      if (
        CSS_DELAY_MS > 0 &&
        relative === 'assets/css/bundle.min.css' &&
        request.headers['x-perf-css-delay'] === '1'
      ) {
        await new Promise((resolve) => setTimeout(resolve, CSS_DELAY_MS));
      }
      const headers = {
        'Content-Type': types[path.extname(file).toLowerCase()] || 'application/octet-stream',
        'Cache-Control': 'no-store',
      };
      if (
        request.headers['accept-encoding']?.includes('gzip') &&
        ['.css', '.html', '.js', '.json', '.svg', '.xml'].includes(path.extname(file).toLowerCase())
      ) {
        body = gzipSync(body);
        headers['Content-Encoding'] = 'gzip';
        headers.Vary = 'Accept-Encoding';
      }
      response.writeHead(200, headers);
      response.end(body);
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(PORT, '127.0.0.1', resolve);
  });
  return server;
}

async function installObservers(page) {
  await page.evaluateOnNewDocument(() => {
    window.__perfAudit = { cls: 0, lcp: null, shifts: [] };
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.hadRecentInput) continue;
        window.__perfAudit.cls += entry.value;
        const sources = (entry.sources || []).map((source) => {
          const node = source.node;
          if (!node) return 'unknown';
          const id = node.id ? `#${node.id}` : '';
          const classes =
            typeof node.className === 'string' && node.className
              ? `.${node.className.trim().split(/\s+/).slice(0, 2).join('.')}`
              : '';
          return `${node.tagName?.toLowerCase() || 'node'}${id}${classes}`;
        });
        window.__perfAudit.shifts.push({ value: entry.value, sources });
      }
    }).observe({ type: 'layout-shift', buffered: true });
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const entry = entries[entries.length - 1];
      const element = entry?.element;
      window.__perfAudit.lcp = entry
        ? {
            value: entry.startTime,
            element: element
              ? `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ''}`
              : 'unknown',
            url: entry.url || '',
          }
        : null;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  });
}

async function singleRun(browser, profileName) {
  const profile = PROFILES[profileName];
  const page = await browser.newPage();
  await page.setViewport(profile.viewport);
  await page.setUserAgent(profile.userAgent);
  if (profile.stability) {
    await page.setExtraHTTPHeaders({ 'x-perf-css-delay': '1' });
  }
  await installObservers(page);

  const failed = [];
  const failedCritical = [];
  page.on('requestfailed', (request) => {
    const url = request.url();
    if (url.endsWith('/favicon.ico')) return;
    const detail = `${request.failure()?.errorText || 'failed'} ${request.resourceType()} ${url}`;
    failed.push(detail);
    if (
      ['document', 'stylesheet', 'script'].includes(request.resourceType()) ||
      url.includes('/assets/images/home/hero-bg-')
    ) {
      failedCritical.push(detail);
    }
  });

  const client = await page.createCDPSession();
  await client.send('Network.enable');
  await client.send('Network.emulateNetworkConditions', {
    offline: false,
    latency: 150,
    downloadThroughput: (1600 * 1024) / 8,
    uploadThroughput: (750 * 1024) / 8,
    connectionType: 'cellular4g',
  });
  await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  await page.goto(BASE_URL, { waitUntil: 'load', timeout: 45_000 });
  await new Promise((resolve) => setTimeout(resolve, 2500));
  const metrics = await page.evaluate(() => ({
    ...window.__perfAudit,
    readyState: document.readyState,
  }));
  await page.close();
  return { ...metrics, failed, failedCritical };
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

function summarize(profile, runs) {
  const cls = median(runs.map((run) => run.cls));
  const lcp = median(runs.map((run) => run.lcp?.value ?? Infinity));
  const failed = runs.reduce((sum, run) => sum + run.failedCritical.length, 0);
  const allFailed = runs.reduce((sum, run) => sum + run.failed.length, 0);
  const representative = runs
    .slice()
    .sort((a, b) => Math.abs(a.cls - cls) - Math.abs(b.cls - cls))[0];
  return {
    profile,
    stability: Boolean(PROFILES[profile].stability),
    cls: Number(cls.toFixed(4)),
    lcpMs: Number.isFinite(lcp) ? Math.round(lcp) : null,
    lcpElement: representative.lcp?.element || 'none',
    lcpUrl: representative.lcp?.url || '',
    failedRequests: failed,
    allFailedRequests: allFailed,
    failedSamples: runs.flatMap((run) => run.failed).slice(0, 3),
    largestShifts: representative.shifts
      .sort((a, b) => b.value - a.value)
      .slice(0, 3),
  };
}

const server = await startServer();
let browser;
try {
  browser = await puppeteer.launch({
    executablePath: await chromePath(),
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });

  const summaries = [];
  for (const profile of Object.keys(PROFILES)) {
    const runs = [];
    for (let run = 0; run < RUNS; run += 1) {
      runs.push(await singleRun(browser, profile));
    }
    summaries.push(summarize(profile, runs));
  }

  console.log(JSON.stringify({ url: BASE_URL, runs: RUNS, summaries }, null, 2));
  const failed = summaries.some(
    (summary) =>
      summary.cls > 0.05 ||
      (!summary.stability && (summary.lcpMs === null || summary.lcpMs > 2500)) ||
      summary.failedRequests > 0,
  );
  if (failed && !REPORT_ONLY) process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  if (server) await new Promise((resolve) => server.close(resolve));
}
