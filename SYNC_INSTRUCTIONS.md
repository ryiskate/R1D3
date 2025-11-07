# Quick Sync Instructions

## ⚠️ Your Sync Button Error

The error "Error checking sync status" happens because:
1. Git commands are failing
2. Your branch has diverged from remote
3. You need to resolve this manually first

## **Fix It Now:**

### Step 1: Stop Server
```bash
# Press Ctrl+C in the terminal running Django
```

### Step 2: Check Status
```bash
git status
```

### Step 3: Resolve Divergence
Your branch and remote have different commits. Choose one:

**Option A: Keep Your Changes (Recommended)**
```bash
git pull --rebase
# If conflicts, resolve them, then:
git add .
git rebase --continue
```

**Option B: Discard Your Changes**
```bash
git fetch origin
git reset --hard origin/master
```

**Option C: Merge (Creates merge commit)**
```bash
git pull
# Resolve any conflicts
git add .
git commit -m "Merged changes"
```

### Step 4: Push Your Changes
```bash
git push
```

### Step 5: Restart Server
```bash
python run_server.py
```

## **After This Fix:**

The sync button will work! But for now, use manual commands:

```bash
# Before working
Ctrl+C              # Stop server
git pull            # Get latest
python run_server.py  # Restart

# After working
Ctrl+C              # Stop server
git add db.sqlite3
git commit -m "Database: your changes"
git push
python run_server.py  # Restart
```

## **Why Manual is Better for Now:**

The sync button is great for simple pulls/pushes, but when there are conflicts or diverged branches, manual Git commands give you more control.

**Once your Git state is clean, the button will work perfectly!**
