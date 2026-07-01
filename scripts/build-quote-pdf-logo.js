const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
let svg = fs.readFileSync(path.join(root, 'assets/images/logo.svg'), 'utf8');
svg = svg.replace(/^<\?xml[^>]*>\s*/i, '');
svg = svg.replace(/<!--[\s\S]*?-->\s*/g, '');
svg = svg.replace(
  /\.st8,\s*\.st3\s*\{\s*fill:\s*#fff;\s*\}/,
  '.st8 { fill: #111827; }\n      .st3 { fill: #fff; }'
);

const out = `/** Abralion PDF logo — embedded SVG (wordmark dark for white PDF bg) */
(function () {
  'use strict';
  window.ABRALION_PDF_LOGO_SVG = ${JSON.stringify(svg)};
  window.ABRALION_PDF_LOGO_ASPECT = ${131.67 / 167.8};

  let cachedLogoDataUrl = '';

  window.ensureAbralionPdfLogoDataUrl = function ensureAbralionPdfLogoDataUrl() {
    if (cachedLogoDataUrl) return Promise.resolve(cachedLogoDataUrl);
    const svgStr = window.ABRALION_PDF_LOGO_SVG || '';
    if (!svgStr) return Promise.resolve('');
    const uri = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgStr);
    return new Promise((resolve) => {
      const loader = new Image();
      loader.onload = () => {
        try {
          const w = 200;
          const h = Math.max(1, Math.round(w * window.ABRALION_PDF_LOGO_ASPECT));
          const canvas = document.createElement('canvas');
          canvas.width = w;
          canvas.height = h;
          canvas.getContext('2d').drawImage(loader, 0, 0, w, h);
          cachedLogoDataUrl = canvas.toDataURL('image/png');
          resolve(cachedLogoDataUrl);
        } catch {
          resolve('');
        }
      };
      loader.onerror = () => resolve('');
      loader.src = uri;
    });
  };
})();
`;

fs.writeFileSync(path.join(root, 'assets/js/quote-pdf-logo.js'), out);
console.log('quote-pdf-logo.js written');
