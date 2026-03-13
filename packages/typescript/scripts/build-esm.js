#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, '../dist');

// Read the compiled .js file (ES2020 module)
const indexPath = path.join(distDir, 'index.js');
const indexContent = fs.readFileSync(indexPath, 'utf-8');

// Write ESM version
const esmPath = path.join(distDir, 'index.mjs');
fs.writeFileSync(esmPath, indexContent);

// Update the CommonJS version to use CommonJS exports
const cjsContent = indexContent
  .replace(/export \{ ([^}]+) \};/g, (match, exports) => {
    const items = exports.split(',').map(s => s.trim());
    const lines = items.map(item => `module.exports.${item} = ${item};`);
    return lines.join('\n');
  })
  .replace(/export (class|interface|type)/g, 'class');

fs.writeFileSync(indexPath, cjsContent);

// Write CommonJS d.ts files
const dtsPath = path.join(distDir, 'index.d.ts');
if (fs.existsSync(dtsPath)) {
  // D.ts files are already correct from tsc
  // Just ensure .d.mts exists for ESM types
  const dtsMtsPath = path.join(distDir, 'index.d.mts');
  const dtsContent = fs.readFileSync(dtsPath, 'utf-8');
  fs.writeFileSync(dtsMtsPath, dtsContent);
}

console.log('✅ Build complete! ESM and CJS outputs ready.');
