# Database Sync Workflow for R1D3 Project

## ⚠️ IMPORTANT: SQLite Database Locking Issue

SQLite databases can only be accessed by one process at a time. When the Django server is running, it locks the database file, preventing Git from updating it during a pull.

---

## **Correct Sync Workflow**

### **Before Starting Work (Pull Latest Changes):**

1. **Stop Django Server:**
   - Press `Ctrl+C` in the terminal running the server
   - Wait for it to fully stop

2. **Sync Database:**
   - Click "Sync Database" button
   - OR run: `git pull`

3. **Restart Django Server:**
   - Run: `python run_server.py`
   - OR: `python manage.py runserver`

### **After Making Changes (Push Your Changes):**

1. **Stop Django Server:**
   - Press `Ctrl+C` in the terminal

2. **Sync Database:**
   - Click "Sync Database" button
   - Enter commit message when prompted
   - OR manually:
     ```bash
     git add db.sqlite3
     git commit -m "Database: Your changes description"
     git push
     ```

3. **Restart Django Server:**
   - Run: `python run_server.py`

---

## **Why This Happens**

- **SQLite locks the database** when Django server is running
- **Git cannot replace** a locked file during `git pull`
- **Solution:** Always stop the server before syncing

---

## **Alternative: Use PostgreSQL (Future)**

For production or if this becomes too annoying, consider switching to PostgreSQL:
- No file locking issues
- Better for multi-user scenarios
- Can sync while server is running
- More robust for concurrent access

But for now, SQLite + Git LFS works fine with the stop/sync/restart workflow!

---

## **Quick Reference**

```bash
# Daily workflow
Ctrl+C              # Stop server
git pull            # Get latest changes
python run_server.py  # Restart server

# After making changes
Ctrl+C              # Stop server
git add db.sqlite3
git commit -m "Database: Added tasks"
git push
python run_server.py  # Restart server
```

---

## **Troubleshooting**

### Error: "unable to unlink old 'db.sqlite3': Invalid argument"
**Cause:** Django server is still running  
**Fix:** Stop the server with Ctrl+C, then try again

### Error: "Merge with strategy ort failed"
**Cause:** Database conflict (both people modified at same time)  
**Fix:** 
1. Stop server
2. Choose version: `git checkout --ours db.sqlite3` or `git checkout --theirs db.sqlite3`
3. Commit: `git add db.sqlite3 && git commit -m "Resolved conflict"`
4. Restart server

### Database seems outdated after pull
**Cause:** Server was running during pull  
**Fix:** Restart the server to reload the database

---

## **Best Practices**

✅ **DO:**
- Always stop server before syncing
- Pull before starting work
- Push at end of work session
- Communicate with your partner about database changes

❌ **DON'T:**
- Try to sync while server is running
- Work on database simultaneously without coordination
- Forget to restart server after pulling

---

**Remember: Stop → Sync → Restart** 🔄
