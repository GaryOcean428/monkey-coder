# AGENTS.md

This document provides key operational guidance for agents working on this repository.

### Railway Deployment Master Cheat Sheet (Reference)
## Common Pitfalls & Correct Solutions

---

## 🔴 **ISSUE 1: Build System Conflicts**

### Common Error Pattern

```text
Nixpacks build failed
ERROR: failed to exec pid1: No such file or directory
```

### Root Cause
Multiple build configurations competing (Dockerfile, railway.toml, railpack.json, nixpacks.toml)

### Correct Solution

```bash
# Railway Build Priority Order (highest to lowest):
# 1. Dockerfile (if exists)
# 2. railpack.json (if exists)
# 3. railway.json/railway.toml
# 4. Nixpacks (auto-detection)

# ENFORCE RAILPACK ONLY:
rm Dockerfile railway.toml nixpacks.toml  # Remove competing configs
touch railpack.json                        # Create railpack config
```

### **Correct railpack.JSON Template:**

```json
{
  "version": "1",
  "metadata": {
    "name": "my-app"
  },
  "build": {
    "provider": "node",  // or "Python"
    "steps": {
      "install": {
        "commands": ["yarn install --frozen-lockfile"]
      },
      "build": {
        "commands": ["yarn build"]
      }
    }
  },
  "deploy": {
    "startCommand": "yarn start",
    "healthCheckPath": "/API/health",
    "healthCheckTimeout": 300
  }
}
```

---

## 🔴 **ISSUE 2: PORT Binding Failures**

### Common Error Pattern

```text
Application failed to respond
Health check failed at /API/health
```

### Root Cause
Apps hardcoding ports or binding to localhost instead of 0.0.0.0

### Correct Solution

#### **Node.js/TypeScript:**

```javascript
// ✅ CORRECT
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';  // NOT 'localhost' or '127.0.0.1'
app.listen(PORT, HOST, () => {
  console.log(`Server running on ${HOST}:${PORT}`);
});

// ❌ WRONG
app.listen(3000);  // Hardcoded port
app.listen(PORT, 'localhost');  // Wrong host
```

#### **Python:**

```python
# ✅ CORRECT
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

# ❌ WRONG
app.run(host="127.0.0.1", port=5000)  # Wrong host and hardcoded port
```

#### railpack.json Start Commands

```json
{
  "deploy": {
    // ✅ CORRECT
    "startCommand": "node server.js",  // Let app read PORT from env

    // ❌ WRONG
    "startCommand": "node server.js --port 3000"  // Hardcoded port
  }
}
```

---

## 🔴 **ISSUE 3: Theme/CSS Loading Issues**

### Common Error Pattern
- Dark mode not persisting
- Tailwind classes not applying
- CSS loading after page render (flash of unstyled content)

### Root Cause
Theme initialization happening after React renders, missing CSS imports

### Correct Solution

#### **1. Pre-React Theme Application:**

```javascript
// src/main.tsx or index.tsx
// ✅ CORRECT - Apply theme BEFORE React renders
document.documentElement.className = localStorage.getItem('theme') || 'dark';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

#### **2. Proper CSS Import Order:**

```css
/* src/index.CSS */
/* ✅ CORRECT ORDER */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Critical theme styles */
.dark {
  color-scheme: dark;
}

/* Your custom styles AFTER Tailwind */
```

#### **3. Vite Config for Railway:**

```javascript
// vite.config.ts
export default defineConfig({
  base: './',  // Relative paths for Railway
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Ensure CSS is bundled
    cssCodeSplit: false
  }
});
```

---

## 🔴 **ISSUE 4: Reference Variable Mistakes**

### **Common Error Pattern:**

```
"Install inputs must be an image or step input"
"serviceA.PORT does not resolve"
```

### **Root Cause:**
Misunderstanding Railway's reference variable system

### **Correct Solution:**

#### **❌ WRONG - Common Mistakes:**

```bash
# Cannot reference PORT of another service
BACKEND_URL=${{backend.PORT}}

# Wrong inputs field in railpack.JSON install step
"install": {
  "inputs": [{"step": "setup"}],  # Install doesn't need inputs
  "commands": ["pip install -r requirements.txt"]
}
```

#### **✅ CORRECT - Proper References:**

```bash
# Reference public domain (Railway provides)
BACKEND_URL=HTTPS://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Reference private domain for internal communication
INTERNAL_API=HTTP://${{backend.RAILWAY_PRIVATE_DOMAIN}}

# Railway automatically provides PORT - don't set manually
# Let Railway inject PORT, app reads from process.env.PORT
```

---

## 🔴 **ISSUE 5: Health Check Configuration**

### **Common Error Pattern:**

```
Health check failed: service unavailable
```

### **Correct Solution:**

#### **1. Add Health Endpoint:**

```javascript
// Express.js
app.get('/API/health', (req, res) => {
  res.status(200).JSON({ status: 'healthy' });
});

// Python Flask
@app.route('/API/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

#### **2. Configure in railpack.JSON:**

```json
{
  "deploy": {
    "healthCheckPath": "/API/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

---

## 🔴 **ISSUE 6: Monorepo Service Confusion**

### **Common Error Pattern:**

```
Nixpacks unable to generate build plan
Multiple services detected
```

### **Correct Solution:**

#### **Separate railpack.JSON for Each Service:**

```bash
# Project structure
/
├── backend/
│   └── railpack.JSON  # Backend-specific config
├── frontend/
│   └── railpack.JSON  # Frontend-specific config
└── railpack.JSON      # Root config (if needed)
```

#### **Root railpack.JSON for Monorepo:**

```json
{
  "version": "1",
  "services": {
    "backend": {
      "root": "./backend",
      "build": {
        "provider": "Python"
      }
    },
    "frontend": {
      "root": "./frontend",
      "build": {
        "provider": "node"
      }
    }
  }
}
```

---

## 📋 **Pre-Deployment Validation Checklist**

```bash
# 1. Check for conflicting build configs
ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml|railpack\.JSON)"

# 2. Validate railpack.JSON syntax
cat railpack.JSON | jq '.' > /dev/null && echo "✅ Valid JSON"

# 3. Verify PORT usage in code
grep -r "process.env.PORT\|PORT" . | grep -v node_modules

# 4. Check host binding
grep -r "0\.0\.0\.0\|localhost\|127\.0\.0\.1" . | grep -E "(listen|HOST|host)"

# 5. Verify health endpoint exists
grep -r "/health\|/API/health" . | grep -v node_modules

# 6. Test build locally
yarn build && PORT=3000 yarn start

# 7. Create git hook for validation
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
if [ -f railpack.JSON ]; then
  jq '.' railpack.JSON > /dev/null || exit 1
fi
EOF
chmod +x .git/hooks/pre-push
```

---

## 🚀 **Quick Fix Commands**

```bash
# Force Railpack rebuild
railway up --force

# Clear Railway build cache
railway run --service <service-name> railway cache:clear

# Debug environment variables
railway run env | grep -E "(PORT|HOST|RAILWAY)"

# Test health endpoint
railway run curl http://localhost:$PORT/api/health
```

---

## 📝 **Add to Your Coding Assistant Rules**

```markdown
## Railway Deployment Standards

1. **Always use railpack.JSON** as the primary build configuration
2. **Never hardcode ports** - always use process.env.PORT
3. **Always bind to 0.0.0.0** not localhost or 127.0.0.1
4. **Apply theme before React renders** to prevent flash of unstyled content
5. **Reference domains not ports** in Railway variables (${{service.RAILWAY_PUBLIC_DOMAIN}})
6. **Include health check endpoint** at /API/health returning 200 status
7. **Remove competing build files** (Dockerfile, railway.toml) when using railpack.JSON
8. **Test locally with Railway environment**: railway run yarn dev
9. **Validate JSON syntax** before committing railpack.JSON
10. **Use inputs field only for layer references** in railpack.JSON, not for basic installs
```

This cheat sheet addresses the recurring issues found across Railway projects. Follow these rules to prevent common pitfalls.
