const fs = require('fs');

const PLAN_FILE = './plan.md';
const SVG_FILE = './progress.svg';

const ROWS = 10;
const COLS = 10;
const TOTAL_PIXELS = ROWS * COLS;

try {
  const planContent = fs.readFileSync(PLAN_FILE, 'utf-8');
  
  const matches = planContent.match(/\\?\[(x| |\/)\\?\]/g) || [];
  const completed = matches.filter(m => m.includes('x')).length;
  const inProgress = matches.filter(m => m.includes('/')).length;
  const total = matches.length || 1;
  const pct = Math.min(100, Math.floor(((completed + (inProgress * 0.5)) / total) * 100));

  const filledPixels = Math.floor((pct / 100) * TOTAL_PIXELS);

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${COLS * 20}" height="${ROWS * 20 + 30}">\n`;
  svg += `<text x="5" y="20" font-family="monospace" font-size="14" fill="#333">Progress: ${pct}%</text>\n`;

  // Color selection logic based on rules
  const baseColor = pct >= 80 ? '#FFD700' : (pct >= 50 ? '#28a745' : '#007BFF');
  const emptyColor = '#e0e0e0';

  for (let i = 0; i < TOTAL_PIXELS; i++) {
    const x = (i % COLS) * 20;
    const y = Math.floor(i / COLS) * 20 + 30; // 30 offset for text
    const fill = i < filledPixels ? baseColor : emptyColor;
    svg += `  <rect x="${x}" y="${y}" width="18" height="18" fill="${fill}" rx="3" />\n`;
  }
  svg += `</svg>`;

  fs.writeFileSync(SVG_FILE, svg, 'utf-8');
  console.log(`Updated progress.svg - ${pct}% complete.`);
} catch (e) {
  console.error("Failed to update progress:", e);
}
