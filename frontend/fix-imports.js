#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Function to calculate relative path
function getRelativePath(fromFile, toModule) {
  const fromDir = path.dirname(fromFile);
  let relativePath = path.relative(fromDir, toModule);
  
  // Ensure we use forward slashes
  relativePath = relativePath.replace(/\\/g, '/');
  
  // Add ./ if it doesn't start with . or ..
  if (!relativePath.startsWith('.')) {
    relativePath = './' + relativePath;
  }
  
  return relativePath;
}

// Map of @ imports to their actual locations
const importMap = {
  '@/lib/utils': 'lib/utils',
  '@/lib/socket': 'lib/socket',
  '@/stores/agentStore': 'stores/agentStore',
  '@/components': 'components'
};

// Find all TypeScript and TSX files
const files = glob.sync('**/*.{ts,tsx}', {
  ignore: ['node_modules/**', '.next/**', 'fix-imports.js']
});

console.log(`Found ${files.length} files to process...`);

let totalReplacements = 0;

files.forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  let modified = false;
  
  // Replace each @ import
  Object.entries(importMap).forEach(([atImport, actualPath]) => {
    const regex = new RegExp(`from ['"]${atImport}(['"/]?)`, 'g');
    
    if (regex.test(content)) {
      content = content.replace(regex, (match, suffix) => {
        const relativePath = getRelativePath(file, actualPath);
        modified = true;
        totalReplacements++;
        console.log(`  ${file}: ${atImport} → ${relativePath}`);
        return `from '${relativePath}${suffix}`;
      });
    }
  });
  
  // Also handle specific component imports like @/components/Something
  const componentRegex = /from ['"]@\/components\/([^'"]+)['"]/g;
  content = content.replace(componentRegex, (match, componentPath) => {
    const relativePath = getRelativePath(file, `components/${componentPath}`);
    modified = true;
    totalReplacements++;
    console.log(`  ${file}: @/components/${componentPath} → ${relativePath}`);
    return `from '${relativePath}'`;
  });
  
  if (modified) {
    fs.writeFileSync(file, content, 'utf8');
  }
});

console.log(`\n✅ Fixed ${totalReplacements} imports across ${files.length} files`);