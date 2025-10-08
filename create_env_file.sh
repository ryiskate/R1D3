#!/bin/bash
# Script to create .env file with MySQL credentials for PythonAnywhere

echo "=== R1D3 .env File Creator ==="
echo ""
echo "This script will help you create a .env file with the correct MySQL credentials."
echo ""
echo "First, go to: https://www.pythonanywhere.com/user/R1D3/databases/"
echo "to find your MySQL credentials."
echo ""

# Get MySQL credentials
read -p "Enter your MySQL username (usually R1D3): " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-R1D3}

read -sp "Enter your MySQL password: " MYSQL_PASSWORD
echo ""

read -p "Enter your MySQL hostname (default: R1D3.mysql.pythonanywhere-services.com): " MYSQL_HOST
MYSQL_HOST=${MYSQL_HOST:-R1D3.mysql.pythonanywhere-services.com}

read -p "Enter your database name (default: R1D3\$default): " DB_NAME
DB_NAME=${DB_NAME:-R1D3\$default}

read -p "Enter your domain (default: r1d3.pythonanywhere.com): " DOMAIN
DOMAIN=${DOMAIN:-r1d3.pythonanywhere.com}

# Create DATABASE_URL
DATABASE_URL="mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}/${DB_NAME}"

# Create .env file
cat > .env << EOL
# Database Configuration
DATABASE_URL=${DATABASE_URL}

# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this-in-production

# Allowed Hosts
ALLOWED_HOSTS=${DOMAIN},localhost,127.0.0.1

# Email Settings (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-email-password
EOL

echo ""
echo "✓ .env file created successfully!"
echo ""
echo "Contents of .env file:"
echo "----------------------------------------"
cat .env
echo "----------------------------------------"
echo ""
echo "Next steps:"
echo "1. Review the .env file to make sure the credentials are correct"
echo "2. Make sure your WSGI file loads the .env file"
echo "3. Restart your web app: touch /var/www/R1D3_pythonanywhere_com_wsgi.py"
