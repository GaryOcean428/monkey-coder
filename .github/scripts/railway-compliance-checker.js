#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class RailwayComplianceChecker {
  constructor() {
    this.issues = [];
    this.checks = {
      'Port Configuration': false,
      'Service URLs': false,
      'CORS Configuration': false,
      'WebSocket Protocol': false,
      'Dockerfile Compliance': false,
      'Environment Variables': false,
    };
  }

  addIssue(severity, file, line, message, suggestion) {
    this.issues.push({
      severity, // 'critical', 'warning', 'info'
      file,
      line,
      message,
      suggestion,
    });
  }

  checkPortConfiguration() {
    const patterns = {
      js: [
        {
          pattern: /app\.listen\s*\(\s*(\d+|['"`]\d+['"`])/g,
          message: 'Hard-coded port found. Use process.env.PORT',
          suggestion: "app.listen(process.env.PORT || 3000, '0.0.0.0')",
        },
        {
          pattern: /app\.listen\s*\([^,)]+\s*\)/g,
          checkFor: '0.0.0.0',
          message: 'Missing host binding. Bind to 0.0.0.0',
          suggestion: "app.listen(process.env.PORT || 3000, '0.0.0.0')",
        },
      ],
      ts: [
        {
          pattern: /app\.listen\s*\(\s*(\d+|['"`]\d+['"`])/g,
          message: 'Hard-coded port found. Use process.env.PORT',
          suggestion: "app.listen(process.env.PORT || 3000, '0.0.0.0')",
        },
      ],
      py: [
        {
          pattern: /app\.run\s*\([^)]*port\s*=\s*(\d+)/g,
          message: 'Hard-coded port in Python app',
          suggestion:
            "app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))",
        },
        {
          pattern: /app\.run\s*\(/g,
          checkFor: 'host=',
          message: 'Missing host binding in Python app',
          suggestion:
            "app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))",
        },
      ],
      json: [
        {
          pattern: /"start":\s*"[^"]*--port\s+\d+/g,
          message: 'Hard-coded port in package.json start script',
          suggestion: '"start": "next start --hostname 0.0.0.0 --port $PORT"',
        },
      ],
    };

    let allPassed = true;

    // Check all relevant files
    const files = this.getRelevantFiles();

    for (const file of files) {
      const ext = path.extname(file).slice(1);
      const filePatterns = patterns[ext] || [];

      if (filePatterns.length === 0) continue;

      const content = fs.readFileSync(file, 'utf8');
      const lines = content.split('\n');

      for (const patternDef of filePatterns) {
        const matches = content.matchAll(patternDef.pattern);

        for (const match of matches) {
          if (patternDef.checkFor) {
            // Check if the required string is missing
            if (!match[0].includes(patternDef.checkFor)) {
              const lineNum = this.getLineNumber(content, match.index);
              this.addIssue(
                'critical',
                file,
                lineNum,
                patternDef.message,
                patternDef.suggestion
              );
              allPassed = false;
            }
          } else {
            // Pattern itself indicates an issue
            const lineNum = this.getLineNumber(content, match.index);
            this.addIssue(
              'critical',
              file,
              lineNum,
              patternDef.message,
              patternDef.suggestion
            );
            allPassed = false;
          }
        }
      }
    }

    this.checks['Port Configuration'] = allPassed;
    return allPassed;
  }

  checkServiceURLs() {
    const badPatterns = [
      {
        pattern: /https?:\/\/localhost(:\d+)?/g,
        message: 'Localhost URL found. Use Railway reference variables',
        suggestion:
          'Use http://${{serviceName.RAILWAY_PRIVATE_DOMAIN}}:${{serviceName.PORT}}',
      },
      {
        pattern: /https?:\/\/127\.0\.0\.1(:\d+)?/g,
        message: '127.0.0.1 URL found. Use Railway reference variables',
        suggestion:
          'Use http://${{serviceName.RAILWAY_PRIVATE_DOMAIN}}:${{serviceName.PORT}}',
      },
      {
        pattern: /https?:\/\/\d+\.\d+\.\d+\.\d+(:\d+)?/g,
        message: 'Hard-coded IP address found',
        suggestion: 'Use Railway service reference variables',
      },
    ];

    let allPassed = true;
    const files = this.getRelevantFiles([
      '.js',
      '.ts',
      '.jsx',
      '.tsx',
      '.py',
      '.env',
      '.json',
    ]);

    for (const file of files) {
      const content = fs.readFileSync(file, 'utf8');

      for (const patternDef of badPatterns) {
        const matches = content.matchAll(patternDef.pattern);

        for (const match of matches) {
          const lineNum = this.getLineNumber(content, match.index);
          this.addIssue(
            'critical',
            file,
            lineNum,
            patternDef.message,
            patternDef.suggestion
          );
          allPassed = false;
        }
      }
    }

    this.checks['Service URLs'] = allPassed;
    return allPassed;
  }

  checkCORSConfiguration() {
    const corsPatterns = [
      {
        pattern: /cors\s*\(\s*\)/g,
        message: 'CORS with no configuration (allows all origins)',
        suggestion:
          'Configure CORS with specific origins: cors({ origin: process.env.FRONTEND_URL, credentials: true })',
      },
      {
        pattern: /origin\s*:\s*['"]\*['"]/g,
        message: 'CORS allows all origins (*) in production',
        suggestion: 'Use specific origins: origin: [process.env.FRONTEND_URL]',
      },
      {
        pattern: /cors\s*\([^)]+\)/g,
        checkFor: 'credentials',
        message: 'CORS configuration missing credentials setting',
        suggestion: 'Add credentials: true if using cookies/auth',
      },
    ];

    let allPassed = true;
    const files = this.getRelevantFiles(['.js', '.ts']);

    for (const file of files) {
      const content = fs.readFileSync(file, 'utf8');

      for (const patternDef of corsPatterns) {
        const matches = content.matchAll(patternDef.pattern);

        for (const match of matches) {
          if (patternDef.checkFor) {
            if (!match[0].includes(patternDef.checkFor)) {
              const lineNum = this.getLineNumber(content, match.index);
              this.addIssue(
                'warning',
                file,
                lineNum,
                patternDef.message,
                patternDef.suggestion
              );
              allPassed = false;
            }
          } else {
            const lineNum = this.getLineNumber(content, match.index);
            this.addIssue(
              'critical',
              file,
              lineNum,
              patternDef.message,
              patternDef.suggestion
            );
            allPassed = false;
          }
        }
      }
    }

    this.checks['CORS Configuration'] = allPassed;
    return allPassed;
  }

  checkWebSocketProtocol() {
    const wsPatterns = [
      {
        pattern: /ws:\/\/[^'"`\s]+/g,
        inFile: /\.(jsx?|tsx?)$/,
        message: 'Using ws:// in client code (should be wss:// for HTTPS)',
        suggestion: 'Use wss:// for secure connections',
      },
      {
        pattern: /new\s+WebSocket\s*\(\s*['"`]ws:/g,
        message: 'WebSocket using insecure protocol',
        suggestion:
          "Use protocol-relative URL or detect HTTPS: new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://...`)",
      },
    ];

    let allPassed = true;
    const files = this.getRelevantFiles(['.js', '.ts', '.jsx', '.tsx']);

    for (const file of files) {
      const content = fs.readFileSync(file, 'utf8');

      for (const patternDef of wsPatterns) {
        if (patternDef.inFile && !patternDef.inFile.test(file)) continue;

        const matches = content.matchAll(patternDef.pattern);

        for (const match of matches) {
          const lineNum = this.getLineNumber(content, match.index);
          this.addIssue(
            'critical',
            file,
            lineNum,
            patternDef.message,
            patternDef.suggestion
          );
          allPassed = false;
        }
      }
    }

    this.checks['WebSocket Protocol'] = allPassed;
    return allPassed;
  }

  checkDockerfile() {
    const dockerfiles = ['Dockerfile', 'dockerfile', 'Dockerfile.prod'];
    let allPassed = true;

    for (const dockerFile of dockerfiles) {
      if (!fs.existsSync(dockerFile)) continue;

      const content = fs.readFileSync(dockerFile, 'utf8');
      const lines = content.split('\n');

      // Check for hard-coded ports
      if (content.match(/EXPOSE\s+\d+/)) {
        const lineNum = lines.findIndex(line => line.match(/EXPOSE\s+\d+/)) + 1;
        this.addIssue(
          'warning',
          dockerFile,
          lineNum,
          'Hard-coded port in EXPOSE instruction',
          'Use ARG PORT and EXPOSE ${PORT}'
        );
        allPassed = false;
      }

      // Check for proper ARG PORT usage
      if (!content.includes('ARG PORT')) {
        this.addIssue(
          'info',
          dockerFile,
          1,
          'Missing ARG PORT declaration',
          'Add ARG PORT at the beginning of Dockerfile'
        );
        allPassed = false;
      }

      // Check CMD for hard-coded ports
      const cmdMatch = content.match(/CMD\s+\[[^\]]*"--port",?\s*"\d+"/);
      if (cmdMatch) {
        const lineNum = this.getLineNumber(content, cmdMatch.index);
        this.addIssue(
          'critical',
          dockerFile,
          lineNum,
          'Hard-coded port in CMD instruction',
          'Use environment variable: CMD ["node", "server.js"]'
        );
        allPassed = false;
      }
    }

    this.checks['Dockerfile Compliance'] = allPassed;
    return allPassed;
  }

  checkEnvironmentVariables() {
    let allPassed = true;

    // Check for railway.toml or railway.json
    const railwayConfig =
      fs.existsSync('railway.toml') || fs.existsSync('railway.json');
    if (!railwayConfig) {
      this.addIssue(
        'info',
        'railway.toml',
        0,
        'No Railway configuration file found',
        'Create railway.toml or railway.json for Railway-specific settings'
      );
    }

    // Check .env.example
    if (fs.existsSync('.env.example')) {
      const envExample = fs.readFileSync('.env.example', 'utf8');

      // Check for Railway-specific variables
      const railwayVars = [
        'RAILWAY_PRIVATE_DOMAIN',
        'RAILWAY_PUBLIC_DOMAIN',
        'PORT',
      ];

      for (const varName of railwayVars) {
        if (!envExample.includes(varName)) {
          this.addIssue(
            'info',
            '.env.example',
            0,
            `Missing ${varName} in .env.example`,
            `Add ${varName}= to document Railway environment variables`
          );
        }
      }
    }

    this.checks['Environment Variables'] = allPassed;
    return allPassed;
  }

  getRelevantFiles(extensions = ['.js', '.ts', '.jsx', '.tsx', '.py']) {
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
          if (extensions.includes(ext) || extensions.length === 0) {
            files.push(fullPath);
          }
        }
      }
    }

    walkDir('.');
    return files;
  }

  getLineNumber(content, index) {
    const lines = content.substring(0, index).split('\n');
    return lines.length;
  }

  generateReport() {
    // Run all checks
    this.checkPortConfiguration();
    this.checkServiceURLs();
    this.checkCORSConfiguration();
    this.checkWebSocketProtocol();
    this.checkDockerfile();
    this.checkEnvironmentVariables();

    const passed =
      this.issues.filter(i => i.severity === 'critical').length === 0;

    return {
      passed,
      timestamp: new Date().toISOString(),
      checks: this.checks,
      issues: this.issues,
      summary: {
        total: this.issues.length,
        critical: this.issues.filter(i => i.severity === 'critical').length,
        warning: this.issues.filter(i => i.severity === 'warning').length,
        info: this.issues.filter(i => i.severity === 'info').length,
      },
    };
  }
}

// Run the checker
const checker = new RailwayComplianceChecker();
const report = checker.generateReport();

// Output JSON report
console.log(JSON.stringify(report, null, 2));

// Exit with error code if critical issues found
if (!report.passed) {
  process.exit(1);
}
