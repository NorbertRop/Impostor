import sharp from 'sharp';
import fs from 'fs';

const createIcon = async (size) => {
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" fill="url(#grad)"/>
  <text x="50%" y="58%" font-family="Arial, sans-serif" font-size="${size * 0.6}" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle">I</text>
</svg>`;

  await sharp(Buffer.from(svg))
    .png()
    .toFile(`public/icon-${size}.png`);
  
  console.log(`Created icon-${size}.png`);
};

(async () => {
  await createIcon(192);
  await createIcon(512);
  // Clean up SVG files
  try {
    fs.unlinkSync('public/icon-192.svg');
    fs.unlinkSync('public/icon-512.svg');
  } catch (e) {}
})();
