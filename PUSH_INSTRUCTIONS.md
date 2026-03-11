# How to Push Your Code to GitHub

## Problem
You're logged in as a different GitHub user (`annya2004`) in Git credentials.

## Solution

### Option 1: Use GitHub Desktop (EASIEST)
1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Sign in with your account: **AniketBhudke**
3. File → Add Local Repository
4. Select the `mitadt_mess` folder
5. Click "Publish repository"
6. Choose repository name: `mitadt-mess-api`
7. Make sure it's **Public**
8. Click "Publish"

✅ Done! Your code will be on GitHub.

---

### Option 2: Clear Git Credentials and Push Again

**Step 1: Clear old credentials**
```bash
# Open Command Prompt and run:
git credential-manager delete https://github.com
```

**Step 2: Set your GitHub username**
```bash
cd mitadt_mess
git config user.name "AniketBhudke"
git config user.email "your-email@example.com"
```

**Step 3: Push to GitHub**
```bash
git remote add origin https://github.com/AniketBhudke/mitadt-mess-api.git
git push -u origin main
```

When prompted:
- Username: `AniketBhudke`
- Password: Use a **Personal Access Token** (not your password)

**How to create Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "mitadt-mess-api"
4. Check: `repo` (all permissions)
5. Click "Generate token"
6. Copy the token (you won't see it again!)
7. Use this token as your password when pushing

---

### Option 3: Use SSH (Advanced)

**Step 1: Generate SSH key**
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

**Step 2: Add SSH key to GitHub**
1. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
2. Go to: https://github.com/settings/keys
3. Click "New SSH key"
4. Paste your key and save

**Step 3: Push using SSH**
```bash
cd mitadt_mess
git remote add origin git@github.com:AniketBhudke/mitadt-mess-api.git
git push -u origin main
```

---

## After Successful Push

Once your code is on GitHub, deploy it:

### Deploy to Render (Free)
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (use AniketBhudke account)
3. Click "New +" → "Web Service"
4. Select "mitadt-mess-api" repository
5. Render auto-detects everything from `render.yaml`
6. Click "Create Web Service"
7. Wait 5-10 minutes
8. Your API will be live at: `https://mitadt-mess-api.onrender.com/api/docs/`

---

## Recommended: Use GitHub Desktop
It's the easiest way and handles all authentication automatically!
