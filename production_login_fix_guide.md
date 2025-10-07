# R1D3 PythonAnywhere Login Fix Guide

This guide will help you fix the 500 error on your PythonAnywhere login page.

## 1. Check Error Logs

First, check the error logs to identify the specific issue:

1. Go to the PythonAnywhere dashboard
2. Click on the "Web" tab
3. Scroll down to the "Logs" section
4. Click on "Error log" to see the most recent errors

## 2. Install Required Packages

Your local environment is missing several packages that are required for authentication. Make sure these are installed on PythonAnywhere:

```bash
pip install mysqlclient python-dotenv django-allauth django-crispy-forms
```

## 3. Configure Database Connection

Make sure your database connection is properly configured:

1. Create a `.env` file in your project root:

```bash
cd ~/R1D3
nano .env
```

2. Add the following content (replace with your actual values):

```
DATABASE_URL=mysql://R1D3:your_password@R1D3.mysql.pythonanywhere-services.com/R1D3$default
DEBUG=False
ALLOWED_HOSTS=R1D3.pythonanywhere.com,localhost,127.0.0.1
```

## 4. Update WSGI File

Make sure your WSGI file loads the environment variables:

1. Go to the PythonAnywhere dashboard
2. Click on the "Web" tab
3. Click on "WSGI configuration file" link
4. Add these lines at the top (after the imports):

```python
from dotenv import load_dotenv
load_dotenv()
```

5. Make sure the settings module is correctly specified:

```python
os.environ['DJANGO_SETTINGS_MODULE'] = 'company_system.settings'
```

## 5. Create a Superuser (if needed)

If you can't log in because there are no users in the database:

```bash
cd ~/R1D3
python manage.py shell
```

Then in the shell:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'secure_password')
exit()
```

## 6. Check Database Tables

Make sure your auth tables are properly created:

```bash
cd ~/R1D3
python manage.py dbshell
```

In the MySQL shell:

```sql
SHOW TABLES LIKE 'auth_%';
SELECT * FROM auth_user;
```

## 7. Restart Your Web App

After making these changes, restart your web app:

```bash
touch /var/www/R1D3_pythonanywhere_com_wsgi.py
```

## 8. Verify Settings

Make sure your production settings are being loaded correctly:

```bash
cd ~/R1D3
python manage.py shell
```

Then in the shell:

```python
from django.conf import settings
print(settings.DATABASES)
print(settings.INSTALLED_APPS)
print(settings.AUTHENTICATION_BACKENDS)
exit()
```

## 9. Check for Database Migration Issues

If your auth tables are not properly created:

```bash
cd ~/R1D3
python manage.py migrate auth
```

## 10. Troubleshooting Common Issues

### Issue: Missing Tables
If your database is missing tables, run:
```bash
python manage.py migrate
```

### Issue: Database Connection Error
Check your DATABASE_URL format and credentials.

### Issue: WSGI Not Loading Settings
Make sure your WSGI file has the correct path to your project.

### Issue: Package Import Errors
Make sure all required packages are installed in your PythonAnywhere virtualenv.
