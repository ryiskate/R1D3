# 📚 Database Sync Guide for 2 Users

## 🎯 Overview
This setup allows two users to share the same database via GitHub, even when not on the same network.

## 🚀 Quick Start

### **Option 1: Manual Sync**

**When you make changes (User 1):**
```bash
python sync_db_push.py
```

**To get changes (User 2):**
```bash
python sync_db_pull.py
```

### **Option 2: Auto-Sync (Recommended)**

**Start auto-sync in a separate terminal:**
```bash
python auto_sync_db.py
```

This automatically pushes database changes to GitHub every 5 seconds when changes are detected.

---

## 📋 Complete Workflow

### **Initial Setup (Both Users - One Time Only)**

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd R1D3
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make sure database is tracked:**
   ```bash
   git add db.sqlite3
   git commit -m "Initial database"
   git push
   ```

---

### **Daily Usage**

#### **User 1 (Making Changes):**

**Terminal 1 - Run Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Auto-sync database:**
```bash
python auto_sync_db.py
```

#### **User 2 (Receiving Changes):**

**Before starting work:**
```bash
python sync_db_pull.py
python manage.py runserver
```

**While working (optional - to get live updates):**
- Stop Django server (Ctrl+C)
- Run: `python sync_db_pull.py`
- Restart: `python manage.py runserver`

---

## ⚠️ Important Notes

1. **Always pull before making changes** to avoid conflicts
2. **Restart Django after pulling** to load the new database
3. **Don't edit simultaneously** - coordinate who's making changes
4. **Watch for conflicts** - Git will warn you if there are merge issues

---

## 🔧 Scripts Explained

- **sync_db_push.py** - Manually push database changes to GitHub
- **sync_db_pull.py** - Manually pull database changes from GitHub  
- **auto_sync_db.py** - Automatically watch and sync database changes

---

## 🐛 Troubleshooting

**"Database is locked" error:**
- Close Django server before pulling
- SQLite only supports one writer at a time

**Git merge conflict:**
- Coordinate with the other user
- Keep one version: `git checkout --theirs db.sqlite3`
- Or yours: `git checkout --ours db.sqlite3`
- Then: `git add db.sqlite3 && git commit`

**Changes not appearing:**
- Make sure auto-sync is running
- Or manually run `python sync_db_push.py`
- Check GitHub to verify the push succeeded
