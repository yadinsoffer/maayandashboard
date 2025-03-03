// prebuild.js
const fs = require('fs');
const path = require('path');

// Ensure directories exist
const ensureDirectoryExists = (dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
};

// The source and destination directories
const srcLibPath = path.join(__dirname, 'src', 'lib');
const nodeModulesPath = path.join(__dirname, 'node_modules', '@');

// Create the node_modules/@/lib directory structure
ensureDirectoryExists(path.join(nodeModulesPath, 'lib'));

// Copy the lib files to node_modules/@/lib
const copyFiles = () => {
  console.log('Copying lib files to ensure module resolution...');
  try {
    // Read all files in the src/lib directory
    const files = fs.readdirSync(srcLibPath);
    
    // Copy each file to node_modules/@/lib
    files.forEach(file => {
      const sourcePath = path.join(srcLibPath, file);
      const destPath = path.join(nodeModulesPath, 'lib', file);
      
      // Copy only if it's a file
      if (fs.statSync(sourcePath).isFile()) {
        fs.copyFileSync(sourcePath, destPath);
        console.log(`Copied ${file} to node_modules/@/lib`);
      }
    });
    
    console.log('All files copied successfully!');
  } catch (error) {
    console.error('Error copying files:', error);
  }
};

// Execute the file copy
copyFiles(); 