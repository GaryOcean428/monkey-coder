# 🚨 RAILWAY DASHBOARD FIX - REQUIRED IMMEDIATELY

## ⚠️ **Critical Issue Identified**

Railway is **completely ignoring** your `railpack.json` files and using **cached/override settings** from the dashboard.

**Proof from your build logs:**
```
Actual command running:  cd packages/web && yarn install --frozen-lockfile
Expected from railpack:  yarn install --immutable (at repo root)

ML service error: "serve: command not found"
Cause: ML service using FRONTEND config instead of railpack-ml.json
```

---

## ✅ **IMMEDIATE ACTION REQUIRED**

### **You Must Fix 3 Things in Railway Dashboard:**

1. ❌ Services have wrong/cached build commands
2. ❌ Services might have wrong root directories  
3. ❌ Services not reading correct config files

---

## 🔧 **Step-by-Step Fix (15 minutes)**

### **Service 1: monkey-coder (Frontend)**

1. **Go to:** Railway Dashboard → monkey-coder project → **monkey-coder** service
2. **Click:** Settings tab
3. **Root Directory:**
   - Current: May show `/packages/web` ❌
   - **Change to:** `/` (just a forward slash) ✅
   - Or **LEAVE BLANK** ✅

4. **Build Command:**
   - If it shows ANYTHING custom ❌
   - **Click "Remove Override"** ✅
   - OR **Delete** the custom command ✅

5. **Start Command:**
   - If it shows `next start` or anything custom ❌
   - **Click "Remove Override"** ✅

6. **Config File:**
   - **Set to:** `railway.json` ✅
   - (New file I just created)

7. **Click SAVE** (if there's a save button)

8. **Go to Deployments tab** → Click **"Deploy"** button

---

### **Service 2: monkey-coder-backend**

1. **Go to:** Railway Dashboard → monkey-coder project → **monkey-coder-backend** service
2. **Click:** Settings tab
3. **Root Directory:** Set to `/` or **LEAVE BLANK**
4. **Build Command:** Remove any overrides
5. **Start Command:** Remove any overrides  
6. **Config File:** Set to `railway-backend.json`
7. **Save and Redeploy**

---

### **Service 3: monkey-coder-ml**

1. **Go to:** Railway Dashboard → monkey-coder project → **monkey-coder-ml** service
2. **Click:** Settings tab
3. **Root Directory:** Set to `/` or **LEAVE BLANK**
4. **Build Command:** Remove any overrides
5. **Start Command:** Remove any overrides
6. **Config File:** Set to `railway-ml.json`
7. **Save and Redeploy**

---

## 📁 **Config Files Now Available**

I've created Railway-specific config files for each service:

| Service | Config File | Purpose |
|---------|-------------|---------|
| **monkey-coder** (frontend) | `railway.json` | Next.js static export with serve |
| **monkey-coder-backend** | `railway-backend.json` | Python FastAPI backend |
| **monkey-coder-ml** | `railway-ml.json` | Python ML inference service |

**All files committed to main branch** ✅

---

## 🔍 **How to Verify Settings in Railway**

For each service, check:

### **Settings Tab Should Show:**

#### **Root Directory:**
```
/ 
(or blank/empty)
```

#### **Build Command:**
```
No custom command
(should show "Not set" or be empty)
```

#### **Start Command:**
```
No custom command  
(should show "Not set" or be empty)
```

#### **Config File:**
```
monkey-coder:         railway.json
monkey-coder-backend: railway-backend.json  
monkey-coder-ml:      railway-ml.json
```

---

## ✅ **Success Indicators After Fix**

Once you've updated all 3 services and redeployed, build logs should show:

### **Frontend (monkey-coder):**
```
✅ corepack enable
✅ yarn install --immutable
✅ yarn workspace @monkey-coder/web build
✅ yarn global add serve
✅ Accepting connections at http://0.0.0.0:XXXX
```

### **Backend (monkey-coder-backend):**
```
✅ python -m venv .venv
✅ pip install -r requirements.txt
✅ uvicorn monkey_coder.app.main:app
✅ Application startup complete
```

### **ML Service (monkey-coder-ml):**
```
✅ python -m venv .venv
✅ pip install -r services/ml/requirements.txt
✅ uvicorn services.ml.ml_server:app
✅ Application startup complete
```

---

## 🚨 **Common Mistakes to Avoid**

1. ❌ **Don't set Root Directory to `/packages/web`**
   - ✅ Use `/` or blank

2. ❌ **Don't leave custom build/start commands**
   - ✅ Remove all overrides

3. ❌ **Don't use `railpack.json` (Railway is ignoring it)**
   - ✅ Use the new `railway.json` files

4. ❌ **Don't forget to redeploy after changing settings**
   - ✅ Click "Deploy" button after saving

---

## 📋 **Quick Checklist**

Complete this for ALL 3 services:

- [ ] **monkey-coder** service:
  - [ ] Root Directory = `/` or blank
  - [ ] Remove build command override
  - [ ] Remove start command override
  - [ ] Config file = `railway.json`
  - [ ] Saved and redeployed

- [ ] **monkey-coder-backend** service:
  - [ ] Root Directory = `/` or blank
  - [ ] Remove build command override
  - [ ] Remove start command override
  - [ ] Config file = `railway-backend.json`
  - [ ] Saved and redeployed

- [ ] **monkey-coder-ml** service:
  - [ ] Root Directory = `/` or blank
  - [ ] Remove build command override
  - [ ] Remove start command override
  - [ ] Config file = `railway-ml.json`
  - [ ] Saved and redeployed

---

## 🆘 **If You Can't Find Settings**

Railway dashboard layout:

1. **Left sidebar:** Select your project
2. **Top:** Select specific service (monkey-coder, monkey-coder-backend, or monkey-coder-ml)
3. **Tabs:** Deployments | Settings | Variables | Metrics
4. **Click "Settings"** tab
5. **Scroll down** to find:
   - Root Directory
   - Build Command
   - Start Command  
   - Config File

---

## ⏱️ **Time Estimate**

- **Per service:** 5 minutes
- **Total for 3 services:** 15 minutes
- **Build + deploy time:** 10-15 minutes
- **Total:** ~30 minutes to fully fixed

---

## 📞 **Still Stuck?**

If after making these changes it still fails:

1. **Screenshot your Railway service settings** (all 3 services)
2. **Share the new build logs** after redeploying
3. **Verify branch:** Check Railway is deploying from `main` branch
4. **Check commits:** Verify latest commits are visible in Railway

---

**Priority:** 🔴 CRITICAL - Must fix before any code changes will work  
**Impact:** All 3 services currently broken  
**Created:** October 8, 2025 05:59 UTC  
**Files Added:** railway.json, railway-backend.json, railway-ml.json
