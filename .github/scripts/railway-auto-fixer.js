#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class RailwayAutoFixer {
  constructor() {
    this.fixCount = 0;
    this.fixes = [];
  }

  log(message) {
    console.log(`[Railway Auto-Fixer] ${message}`);
    this.fixes.push(message);
  }

  fixFile(filePath, fixes) {
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      let modified = false;

      for (const fix of fixes) {
        const result = fix(content);
        if (result !== content) {
          content = result;
          modified = true;
          this.fixCount++;
        }
      }

      if (modified) {
        fs.writeFileSync(filePath, content, 'utf8');
        this.log(`Fixed ${filePath}`);
      }

      return modified;
    } catch (error) {
      console.error(`Error fixing ${filePath}:`, error);
      return false;
    }
  }

  fixPortConfiguration() {
    const fixes = {
      // Node.js/Express fixes
      '.js': [
        {
          // Fix hard-coded ports
          pattern: /app\.listen\s*\(\s*(\d+|['"`]\d+['"`])\s*\)/g,
          replacement: "app.listen(process.env.PORT || 3000, '0.0.0.0')",
          description: 'Replace hard-coded port with process.env.PORT',
        },
        {
          // Add host binding if missing
          pattern: /app\.listen\s*\(\s*(process\.env\.PORT[^,)]*)\s*\)/g,
          replacement: "app.listen($1, '0.0.0.0')",
          description: 'Add 0.0.0.0 host binding',
        },
      ],
      '.ts': [
        {
          pattern: /app\.listen\s*\(\s*(\d+|['"`]\d+['"`])\s*\)/g,
          replacement: "app.listen(process.env.PORT || 3000, '0.0.0.0')",
          description: 'Replace hard-coded port with process.env.PORT',
        },
      ],
      '.py': [
        {
          // Fix Flask/Python apps
          pattern: /app\.run\s*\(\s*port\s*=\s*(\d+)\s*\)/g,
          replacement:
            "app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))",
          description: 'Fix Python app port configuration',
        },
        {
          // Add host if missing
          pattern: /app\.run\s*\(\s*\)/g,
          replacement:
            "app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))",
          description: 'Add host and port configuration to Python app',
        },
      ],
    };

    for (const [ext, fixPatterns] of Object.entries(fixes)) {
      const files = this.findFiles(ext);

      for (const file of files) {
        const fileFixes = fixPatterns.map(fix => content => {
          if (content.match(fix.pattern)) {
            this.log(`${fix.description} in ${file}`);
            return content.replace(fix.pattern, fix.replacement);
          }
          return content;
        });

        this.fixFile(file, fileFixes);
      }
    }
  }

  fixServiceURLs() {
    const urlFixes = [
      {
        pattern: /http:\/\/localhost(:\d+)?/g,
        replacement: (match, port) => {
          // Try to determine service name from context
          return `process.env.API_URL || 'http://localhost${port || ''}'`;
        },
        description: 'Replace localhost URLs with environment variables',
      },
      {
        pattern: /https?:\/\/127\.0\.0\.1(:\d+)?/g,
        replacement: (match, port) => {
          return `process.env.API_URL || '${match}'`;
        },
        description: 'Replace 127.0.0.1 URLs with environment variables',
      },
    ];

    const files = this.findFiles('.js', '.ts', '.jsx', '.tsx', '.json');

    for (const file of files) {
      // Skip test files
      if (file.includes('test') || file.includes('spec')) continue;

      const fixes = urlFixes.map(fix => content => {
        if (content.match(fix.pattern)) {
          this.log(`${fix.description} in ${file}`);
          return content.replace(fix.pattern, fix.replacement);
        }
        return content;
      });

      this.fixFile(file, fixes);
    }
  }

  fixPackageJsonScripts() {
    const packageJsonPath = 'package.json';

    if (fs.existsSync(packageJsonPath)) {
      try {
        const packageJson = JSON.parse(
          fs.readFileSync(packageJsonPath, 'utf8')
        );
        let modified = false;

        // Fix start scripts
        if (packageJson.scripts) {
          for (const [scriptName, scriptValue] of Object.entries(
            packageJson.scripts
          )) {
            // Fix Next.js start scripts
            if (
              scriptValue.includes('next start') &&
              scriptValue.includes('--port')
            ) {
              const newScript = scriptValue.replace(
                /--port\s+\d+/,
                '--port $PORT'
              );
              if (!scriptValue.includes('--hostname')) {
                packageJson.scripts[scriptName] = newScript.replace(
                  'next start',
                  'next start --hostname 0.0.0.0'
                );
              } else {
                packageJson.scripts[scriptName] = newScript;
              }
              modified = true;
              this.log(`Fixed Next.js start script in package.json`);
            }

            // Fix other Node.js start scripts
            if (scriptValue.includes('node') && scriptValue.includes('PORT=')) {
              packageJson.scripts[scriptName] = scriptValue.replace(
                /PORT=\d+/,
                'PORT=$PORT'
              );
              modified = true;
              this.log(
                `Fixed PORT variable in package.json script: ${scriptName}`
              );
            }
          }
        }

        if (modified) {
          fs.writeFileSync(
            packageJsonPath,
            JSON.stringify(packageJson, null, 2) + '\n'
          );
          this.fixCount++;
        }
      } catch (error) {
        console.error('Error fixing package.json:', error);
      }
    }
  }

  fixDockerfile() {
    const dockerfiles = ['Dockerfile', 'dockerfile', 'Dockerfile.prod'];

    for (const dockerFile of dockerfiles) {
      if (!fs.existsSync(dockerFile)) continue;

      const fixes = [
        {
          // Fix EXPOSE with hard-coded port
          pattern: /EXPOSE\s+(\d+)/g,
          replacement: (match, port) => {
            // Add ARG PORT if not present
            return 'EXPOSE ${PORT:-' + port + '}';
          },
          description: 'Replace hard-coded EXPOSE with variable',
        },
        {
          // Fix CMD with hard-coded port
          pattern: /CMD\s+\[([^\]]*)"--port",?\s*"(\d+)"([^\]]*)\]/g,
          replacement: 'CMD [$1$3]',
          description: 'Remove hard-coded port from CMD',
        },
      ];

      const content = fs.readFileSync(dockerFile, 'utf8');
      let newContent = content;

      // Add ARG PORT if missing
      if (!content.includes('ARG PORT')) {
        newContent = 'ARG PORT\n' + newContent;
        this.log(`Added ARG PORT to ${dockerFile}`);
      }

      // Apply fixes
      for (const fix of fixes) {
        if (newContent.match(fix.pattern)) {
          newContent = newContent.replace(fix.pattern, fix.replacement);
          this.log(`${fix.description} in ${dockerFile}`);
        }
      }

      if (newContent !== content) {
        fs.writeFileSync(dockerFile, newContent);
        this.fixCount++;
      }
    }
  }

  fixEnvExample() {
    const envExamplePath = '.env.example';

    if (!fs.existsSync(envExamplePath)) {
      // Create .env.example with Railway variables
      const railwayEnvVars = [
        '# Railway Environment Variables',
        'PORT=',
        'RAILWAY_PUBLIC_DOMAIN=',
        'RAILWAY_PRIVATE_DOMAIN=',
        '',
        '# Application Environment Variables',
        'NODE_ENV=production',
        'API_URL=',
        'FRONTEND_URL=',
        '',
      ].join('\n');

      fs.writeFileSync(envExamplePath, railwayEnvVars);
      this.log('Created .env.example with Railway variables');
      this.fixCount++;
    } else {
      // Add missing Railway variables
      let content = fs.readFileSync(envExamplePath, 'utf8');
      let modified = false;

      const requiredVars = [
        'PORT',
        'RAILWAY_PUBLIC_DOMAIN',
        'RAILWAY_PRIVATE_DOMAIN',
      ];

      for (const varName of requiredVars) {
        if (!content.includes(varName)) {
          content += `\n${varName}=`;
          modified = true;
          this.log(`Added ${varName} to .env.example`);
        }
      }

      if (modified) {
        fs.writeFileSync(envExamplePath, content);
        this.fixCount++;
      }
    }
  }

  fixCORSConfiguration() {
    const files = this.findFiles('.js', '.ts');

    for (const file of files) {
      const content = fs.readFileSync(file, 'utf8');

      // Only fix files that use cors
      if (!content.includes('cors(')) continue;

      const fixes = [
        {
          // Fix cors() with no config
          pattern: /app\.use\s*\(\s*cors\s*\(\s*\)\s*\)/g,
          replacement: `app.use(cors({
  origin: process.env.FRONTEND_URL || true,
  credentials: true
}))`,
          description: 'Add CORS configuration',
        },
        {
          // Fix cors with wildcard origin
          pattern: /origin\s*:\s*['"]\*['"]/g,
          replacement: 'origin: process.env.FRONTEND_URL || true',
          description: 'Replace wildcard CORS origin with environment variable',
        },
      ];

      const fileFixes = fixes.map(fix => content => {
        if (content.match(fix.pattern)) {
          this.log(`${fix.description} in ${file}`);
          return content.replace(fix.pattern, fix.replacement);
        }
        return content;
      });

      this.fixFile(file, fileFixes);
    }
  }

  findFiles(...extensions) {
    const files = [];
    const ignorePaths = [
      'node_modules',
      '.git',
      'dist',
      'build',
      '.next',
      '__pycache__',
    ];

    function walkDir(dir) {
      const items = fs.readdirSync(dir);

      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
          if (!ignorePaths.includes(item)) {
            walkDir(fullPath);
          }
        } else if (stat.isFile()) {
          const ext = path.extname(item);
          if (extensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    }

    walkDir('.');
    return files;
  }

  run() {
    this.log('Starting Railway compliance auto-fixes...');

    // Run all fixes
    this.fixPortConfiguration();
    this.fixServiceURLs();
    this.fixPackageJsonScripts();
    this.fixDockerfile();
    this.fixEnvExample();
    this.fixCORSConfiguration();

    this.log(`\nCompleted with ${this.fixCount} fixes applied.`);

    // Write fix report
    const report = {
      timestamp: new Date().toISOString(),
      fixCount: this.fixCount,
      fixes: this.fixes,
    };

    fs.writeFileSync(
      'railway-fixes-report.json',
      JSON.stringify(report, null, 2)
    );
  }
}

// Run the auto-fixer
const fixer = new RailwayAutoFixer();
fixer.run();
