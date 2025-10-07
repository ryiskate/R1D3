# Freeing Up Space on PythonAnywhere

If you're encountering "Disk quota exceeded" errors, follow these steps to free up space on your PythonAnywhere account.

## 1. Check Your Current Disk Usage

```bash
du -sh ~
```

This shows your total disk usage. PythonAnywhere free accounts have a limit of 512MB.

## 2. Find Large Files and Directories

```bash
du -h --max-depth=1 ~ | sort -hr
```

This will show directories sorted by size.

## 3. Common Files to Clean Up

### Remove Unused Virtualenvs

```bash
rm -rf ~/.virtualenvs/unused_venv_name
```

### Clean Python Cache Files

```bash
find ~ -name "__pycache__" -type d -exec rm -rf {} +
find ~ -name "*.pyc" -delete
```

### Remove Old Log Files

```bash
rm -f ~/logs/*.log.*
```

### Clean Package Cache

```bash
pip cache purge
```

### Remove Old Database Backups

```bash
rm -f ~/backups/*.sql
```

## 4. Clean Git Repository

If your git repository is taking up too much space:

```bash
cd ~/your_project
git gc --aggressive
```

Or for a more thorough cleanup:

```bash
cd ~/your_project
rm -rf .git
git init
git remote add origin https://github.com/ryiskate/R1D3.git
git fetch
git checkout -b master --track origin/master
```

## 5. Directly Fix Login Issues Without Pulling

Since you can't pull the repository due to disk space issues, here are the direct steps to fix your login issues:

### Install Required Packages

```bash
pip install mysqlclient python-dotenv django-allauth django-crispy-forms
```

### Create .env File

```bash
cd ~/R1D3
echo "DATABASE_URL=mysql://R1D3:your_password@R1D3.mysql.pythonanywhere-services.com/R1D3\$default" > .env
echo "DEBUG=False" >> .env
echo "ALLOWED_HOSTS=R1D3.pythonanywhere.com,localhost,127.0.0.1" >> .env
```

### Update WSGI File

Edit your WSGI file to add:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Restart Web App

```bash
touch /var/www/R1D3_pythonanywhere_com_wsgi.py
```

## 6. Consider Upgrading Your Account

If you're consistently running into disk quota issues, consider upgrading your PythonAnywhere account for more storage space.
