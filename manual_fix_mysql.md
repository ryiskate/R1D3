# Manual Fix for MySQL Credentials on PythonAnywhere

Since you're encountering an "Access denied" error for your MySQL database, follow these steps to fix it manually:

## Step 1: Find Your Correct MySQL Credentials

1. Go to the PythonAnywhere dashboard
2. Click on the "Databases" tab
3. Note the following information:
   - Your MySQL username (usually your PythonAnywhere username)
   - Your MySQL password (what you set when creating the database)
   - Your MySQL hostname (usually `username.mysql.pythonanywhere-services.com`)
   - Your database name (usually `username$default`)

## Step 2: Create or Update Your .env File

Create a new `.env` file with the correct credentials:

```bash
cd ~/R1D3
cat > .env << EOL
DATABASE_URL=mysql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOSTNAME/YOUR_DATABASE_NAME
DEBUG=False
ALLOWED_HOSTS=r1d3.pythonanywhere.com,localhost,127.0.0.1
EOL
```

Replace:
- `YOUR_USERNAME` with your MySQL username
- `YOUR_PASSWORD` with your MySQL password
- `YOUR_HOSTNAME` with your MySQL hostname
- `YOUR_DATABASE_NAME` with your database name (remember to escape the $ character with a backslash if needed)

Example:
```bash
cat > .env << EOL
DATABASE_URL=mysql://R1D3:my_secure_password@R1D3.mysql.pythonanywhere-services.com/R1D3\$default
DEBUG=False
ALLOWED_HOSTS=r1d3.pythonanywhere.com,localhost,127.0.0.1
EOL
```

## Step 3: Test Your MySQL Connection

Test if your credentials are correct:

```bash
mysql -u YOUR_USERNAME -p -h YOUR_HOSTNAME
```

When prompted, enter your MySQL password. If you can connect successfully, your credentials are correct.

## Step 4: Make Sure Your WSGI File Loads the .env File

Edit your WSGI file:

```bash
nano /var/www/R1D3_pythonanywhere_com_wsgi.py
```

Add these lines after the imports:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 5: Restart Your Web App

```bash
touch /var/www/R1D3_pythonanywhere_com_wsgi.py
```

## Step 6: Check the Error Logs Again

If you still encounter issues, check the error logs for new errors:

1. Go to the PythonAnywhere dashboard
2. Click on the "Web" tab
3. Scroll down to the "Logs" section
4. Click on "Error log" to see the most recent errors
