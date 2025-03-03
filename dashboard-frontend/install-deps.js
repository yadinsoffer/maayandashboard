const { execSync } = require('child_process');

console.log('Installing babel-plugin-module-resolver...');
try {
  execSync('npm install --save-dev babel-plugin-module-resolver', {
    stdio: 'inherit'
  });
  console.log('Successfully installed babel-plugin-module-resolver!');
} catch (error) {
  console.error('Failed to install dependencies:', error);
  process.exit(1);
} 