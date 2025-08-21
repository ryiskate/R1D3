# PythonAnywhere Deployment Instructions for R1D3

## Prerequisites

1. **PythonAnywhere Account**: Ensure you have a PythonAnywhere account with MySQL database access
2. **Git Repository**: Your R1D3 code should be in a Git repository (GitHub, GitLab, etc.)
3. **MySQL Database**: Set up a MySQL database in PythonAnywhere's Databases tab

## Step 1: Prepare the Deployment Script

1. **Edit the deployment script** (`deploy_to_pythonanywhere.sh`):
   ```bash
   # Update these variables at the top of the script:
   PYTHONANYWHERE_USERNAME="your_actual_username"
   DOMAIN_NAME="your_actual_domain.pythonanywhere.com"
   REPO_URL="https://github.com/yourusername/R1D3.git"
   ```

2. **Make the script executable**:
   ```bash
   chmod +x deploy_to_pythonanywhere.sh
   ```

## Step 2: Upload and Run the Script

1. **Upload the script** to your PythonAnywhere account:
   - Use the Files tab in PythonAnywhere dashboard
   - Upload `deploy_to_pythonanywhere.sh` to your home directory

2. **Open a Bash console** in PythonAnywhere and run:
   ```bash
   ./deploy_to_pythonanywhere.sh
   ```

## Step 3: Configure Database Credentials

After running the script, **edit the `.env` file** in your project directory:

```bash
nano ~/R1D3/.env
```

Update the DATABASE_URL with your actual MySQL credentials:
```
DATABASE_URL=mysql://username:password@hostname:port/database_name
```

You can find these credentials in PythonAnywhere's **Databases** tab.

## Step 4: Configure Web App Settings

In PythonAnywhere's **Web** tab:

1. **Set Python version**: Python 3.11
2. **Set source code path**: `/home/yourusername/R1D3`
3. **Set working directory**: `/home/yourusername/R1D3`
4. **Configure static files mapping**:
   - URL: `/static/`
   - Directory: `/home/yourusername/R1D3/staticfiles/`
5. **Configure media files mapping** (if needed):
   - URL: `/media/`
   - Directory: `/home/yourusername/R1D3/media/`

## Step 5: Environment Variables

Ensure these environment variables are set in your `.env` file:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.pythonanywhere.com,yourusername.pythonanywhere.com
DATABASE_URL=mysql://username:password@hostname:port/database_name
```

## Step 6: Final Steps

1. **Reload your web app** in the Web tab
2. **Test your application** by visiting your domain
3. **Check error logs** if there are any issues

## Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Verify DATABASE_URL format
   - Check MySQL credentials in Databases tab

2. **Static Files Not Loading**:
   - Ensure static files mapping is correct
   - Run `python manage.py collectstatic` again

3. **Import Errors**:
   - Check that all dependencies are installed in virtual environment
   - Verify PYTHONPATH in WSGI file

4. **500 Internal Server Error**:
   - Check error logs in Web tab
   - Verify all environment variables are set correctly

### Useful Commands:

```bash
# Activate virtual environment
source ~/venv_R1D3/bin/activate

# Check database connection
cd ~/R1D3
python manage.py check --database default

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

## Rollback Procedure

If deployment fails, you can rollback using the backup:

1. **Find your backup**:
   ```bash
   ls ~/backups/
   ```

2. **Restore from backup**:
   ```bash
   cp -r ~/backups/YYYYMMDD_HHMMSS/R1D3 ~/R1D3_backup
   mv ~/R1D3 ~/R1D3_failed
   mv ~/R1D3_backup ~/R1D3
   ```

3. **Reload web app** in PythonAnywhere Web tab

## Security Notes

- Never commit `.env` files to version control
- Use strong SECRET_KEY in production
- Regularly update dependencies
- Monitor application logs for security issues
- Keep DEBUG=False in production

## Support

If you encounter issues:
1. Check PythonAnywhere's help documentation
2. Review error logs in the Web tab
3. Test database connectivity using the console
4. Verify all file permissions are correct
