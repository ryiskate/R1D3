# Git LFS Quick Start Guide for R1D3 Project

## ✅ Setup Complete!

Git LFS is now configured to track:
- **Images:** `*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.bmp`, `*.webp`, `*.svg`, `*.ico`
- **Videos:** `*.mp4`, `*.mov`, `*.avi`, `*.mkv`, `*.webm`
- **Audio:** `*.mp3`, `*.wav`, `*.ogg`
- **Database:** `*.db`, `*.sqlite3`, `*.sqlite`
- **Archives:** `*.pdf`, `*.zip`, `*.rar`, `*.7z`

---

## For the Second Person (First Time Setup)

When cloning the repository for the first time:

```bash
# 1. Install Git LFS (one-time setup)
git lfs install

# 2. Clone the repository (LFS files will download automatically)
git clone https://github.com/yourusername/R1D3.git
cd R1D3

# 3. Verify LFS files were downloaded
git lfs ls-files
```

---

## Daily Workflow (Both People)

### Pulling Changes
```bash
# Pull code and LFS files
git pull

# If LFS files didn't download automatically:
git lfs pull
```

### Committing Changes
```bash
# Add your changes (LFS files are handled automatically)
git add .

# Commit
git commit -m "Your commit message"

# Push (this will push LFS files too)
git push
```

---

## Working with the Database

Since `db.sqlite3` is tracked by LFS, both people will sync the same database automatically!

### **Easy Way: Use the Sync Script**

Just run this script before and after working:

```bash
# Windows
sync_database.bat

# It will:
# - Pull latest database changes
# - Commit and push your changes (if any)
# - Warn you if database was updated
```

### **Manual Way:**

**Before Making Database Changes:**
```bash
# Always pull first to get latest database
git pull
```

**After Making Database Changes:**
```bash
# Commit and push the database
git add db.sqlite3
git commit -m "Database: Added 3 tasks for Ricardo, updated Epic status"
git push
```

### **Handling Database Conflicts:**

If both people modify the database at the same time:

**Option 1: Keep your version**
```bash
git checkout --ours db.sqlite3
git add db.sqlite3
git commit -m "Resolved database conflict - kept local changes"
```

**Option 2: Keep their version**
```bash
git checkout --theirs db.sqlite3
git add db.sqlite3
git commit -m "Resolved database conflict - kept remote changes"
```

**Option 3: Manual merge** (recommended if both changes are important)
1. Backup your database: `copy db.sqlite3 db_backup.sqlite3`
2. Export your changes: `python manage.py dumpdata projects.R1D3Task > my_tasks.json`
3. Pull their version: `git pull`
4. Re-apply your changes manually or: `python manage.py loaddata my_tasks.json`

---

## Checking LFS Status

### See which files are tracked by LFS:
```bash
git lfs ls-files
```

### See LFS storage usage:
```bash
git lfs ls-files -s
```

### Check if a file is using LFS:
```bash
git lfs ls-files | grep filename
```

---

## Troubleshooting

### LFS files not downloading?
```bash
# Force download all LFS files
git lfs fetch --all
git lfs checkout
```

### Push failing due to LFS bandwidth limit?
GitHub free tier includes:
- 1GB storage
- 1GB bandwidth per month

If exceeded, you can:
1. Wait until next month
2. Upgrade to GitHub Pro ($4/month for 50GB)
3. Switch to self-hosted server (see SELF_HOSTED_GIT_SERVER_GUIDE.md)

### Check your LFS usage:
Visit: `https://github.com/yourusername/R1D3/settings`
→ Look for "Git LFS Data" section

---

## Best Practices

### ✅ DO:
- Pull before starting work
- Commit database changes with descriptive messages
- Push regularly (at least daily)
- Communicate when making major database changes

### ❌ DON'T:
- Work on the database simultaneously without coordination
- Commit huge files without checking LFS is tracking them
- Force push (`git push --force`) - you'll lose LFS history

---

## Communication Protocol

When making significant database changes:

1. **Before:** Message the other person: "Working on database - adding new tasks"
2. **During:** Make your changes
3. **After:** Commit and push immediately
4. **Notify:** "Database updated - please pull"

This prevents conflicts and keeps everyone in sync!

---

## File Size Limits

GitHub LFS limits:
- **Max file size:** 2GB per file
- **Repository size:** No hard limit, but keep it reasonable

If you need to store files larger than 2GB:
- Split them into smaller parts
- Use external storage (OneDrive/Google Drive)
- Switch to self-hosted server

---

## Quick Commands Reference

```bash
# Check LFS status
git lfs status

# List LFS files
git lfs ls-files

# Download specific LFS file
git lfs pull --include="path/to/file.png"

# Download all LFS files
git lfs pull

# See LFS file history
git lfs logs last

# Verify LFS installation
git lfs version

# Re-initialize LFS (if having issues)
git lfs install --force
```

---

## Next Steps

1. ✅ Git LFS is configured
2. 📤 Push your changes: `git push`
3. 👥 Share repository URL with collaborator
4. 📖 Collaborator follows "For the Second Person" section above
5. 🚀 Start collaborating!

---

## Need Help?

- **Git LFS Docs:** https://git-lfs.github.com/
- **GitHub LFS Guide:** https://docs.github.com/en/repositories/working-with-files/managing-large-files
- **Self-Hosted Option:** See `SELF_HOSTED_GIT_SERVER_GUIDE.md`

---

**Remember:** Git LFS makes large files work like regular Git files. Just `add`, `commit`, and `push` as usual! 🎉
