#!/bin/bash

# PythonAnywhere Deployment Script for R1D3 Django Application
# This script deploys the updated R1D3 application to PythonAnywhere with PostgreSQL database

set -e  # Exit on any error

# Configuration - UPDATE THESE VALUES FOR YOUR PYTHONANYWHERE SETUP
PYTHONANYWHERE_USERNAME="your_username"  # Replace with your PythonAnywhere username
DOMAIN_NAME="your_domain.pythonanywhere.com"  # Replace with your domain
PROJECT_NAME="R1D3"
REPO_URL="https://github.com/yourusername/R1D3.git"  # Replace with your repo URL
BRANCH="main"  # or master, depending on your default branch

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're running on PythonAnywhere
check_environment() {
    log "Checking environment..."
    if [[ ! "$HOSTNAME" == *"pythonanywhere"* ]]; then
        warning "This script is designed to run on PythonAnywhere servers."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    success "Environment check completed"
}

# Function to backup current application
backup_current_app() {
    log "Creating backup of current application..."
    
    BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ -d "$HOME/$PROJECT_NAME" ]; then
        cp -r "$HOME/$PROJECT_NAME" "$BACKUP_DIR/"
        success "Backup created at: $BACKUP_DIR"
    else
        warning "No existing application found to backup"
    fi
}

# Function to setup virtual environment
setup_virtualenv() {
    log "Setting up virtual environment..."
    
    cd "$HOME"
    
    # Remove old virtual environment if it exists
    if [ -d "venv_$PROJECT_NAME" ]; then
        log "Removing old virtual environment..."
        rm -rf "venv_$PROJECT_NAME"
    fi
    
    # Create new virtual environment
    python3.11 -m venv "venv_$PROJECT_NAME"
    source "venv_$PROJECT_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    success "Virtual environment created and activated"
}

# Function to clone or update repository
update_code() {
    log "Updating application code..."
    
    cd "$HOME"
    
    if [ -d "$PROJECT_NAME" ]; then
        log "Updating existing repository..."
        cd "$PROJECT_NAME"
        git fetch origin
        git reset --hard "origin/$BRANCH"
        git clean -fd
    else
        log "Cloning repository..."
        git clone -b "$BRANCH" "$REPO_URL" "$PROJECT_NAME"
        cd "$PROJECT_NAME"
    fi
    
    success "Code updated successfully"
}

# Function to install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/venv_$PROJECT_NAME/bin/activate"
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        error "requirements.txt not found!"
        exit 1
    fi
    
    # Install additional production dependencies
    pip install mysqlclient gunicorn dj-database-url python-dotenv whitenoise
    
    success "Dependencies installed successfully"
}

# Function to setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    cd "$HOME/$PROJECT_NAME"
    
    # Create .env file for production
    cat > .env << EOF
# Production Environment Variables for PythonAnywhere
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=$DOMAIN_NAME,$PYTHONANYWHERE_USERNAME.pythonanywhere.com,localhost,127.0.0.1

# MySQL Database Configuration
# Replace these with your actual MySQL credentials from PythonAnywhere
DATABASE_URL=mysql://username:password@hostname:port/database_name

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static files
STATIC_URL=/static/
STATIC_ROOT=/home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME/staticfiles/
EOF
    
    warning "IMPORTANT: Edit the .env file with your actual database credentials!"
    warning "You can find your MySQL details in the PythonAnywhere Databases tab"
    
    success "Environment file created"
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/venv_$PROJECT_NAME/bin/activate"
    
    # Check database connection
    python manage.py check --database default
    
    # Run migrations
    python manage.py migrate --noinput
    
    success "Database migrations completed"
}

# Function to collect static files
collect_static() {
    log "Collecting static files..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/venv_$PROJECT_NAME/bin/activate"
    
    # Create staticfiles directory
    mkdir -p staticfiles
    
    # Collect static files
    python manage.py collectstatic --noinput --clear
    
    success "Static files collected"
}

# Function to seed database with initial data
seed_database() {
    log "Seeding database with initial data..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/venv_$PROJECT_NAME/bin/activate"
    
    read -p "Do you want to seed the database with admin users and initial data? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Run the production seeding script
        python seed_production_db.py
        success "Database seeded with initial data"
        warning "IMPORTANT: Change all default passwords after first login!"
    else
        log "Skipping database seeding"
        # Offer manual superuser creation
        read -p "Create a superuser manually? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python manage.py createsuperuser
            success "Superuser created"
        fi
    fi
}

# Function to update WSGI configuration
update_wsgi_config() {
    log "Updating WSGI configuration..."
    
    # Create WSGI file
    cat > "$HOME/var/www/${PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py" << EOF
import os
import sys

# Add your project directory to the sys.path
path = '/home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'company_system.settings'

# Activate virtual environment
activate_this = '/home/$PYTHONANYWHERE_USERNAME/venv_$PROJECT_NAME/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF
    
    success "WSGI configuration updated"
}

# Function to restart web app
restart_webapp() {
    log "Restarting web application..."
    
    # Touch the WSGI file to restart the app
    touch "$HOME/var/www/${PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py"
    
    success "Web application restarted"
}

# Function to run tests
run_tests() {
    log "Running application tests..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/venv_$PROJECT_NAME/bin/activate"
    
    read -p "Do you want to run tests? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py test --verbosity=2
        success "Tests completed"
    else
        log "Skipping tests"
    fi
}

# Function to display post-deployment instructions
post_deployment_instructions() {
    echo
    success "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
    echo
    log "Post-deployment checklist:"
    echo "1. Update your .env file with actual database credentials"
    echo "2. Configure static files mapping in PythonAnywhere web tab:"
    echo "   URL: /static/"
    echo "   Directory: /home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME/staticfiles/"
    echo "3. Configure media files mapping (if needed):"
    echo "   URL: /media/"
    echo "   Directory: /home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME/media/"
    echo "4. Check your web app is running at: https://$DOMAIN_NAME"
    echo "5. Monitor error logs in PythonAnywhere web tab if issues occur"
    echo
    warning "IMPORTANT: Make sure to update your PostgreSQL database credentials in .env!"
    echo
}

# Main deployment function
main() {
    log "Starting R1D3 deployment to PythonAnywhere..."
    echo
    
    # Validate configuration
    if [[ "$PYTHONANYWHERE_USERNAME" == "your_username" ]]; then
        error "Please update the configuration variables at the top of this script!"
        exit 1
    fi
    
    # Run deployment steps
    check_environment
    backup_current_app
    setup_virtualenv
    update_code
    install_dependencies
    setup_environment
    run_migrations
    collect_static
    seed_database
    update_wsgi_config
    run_tests
    restart_webapp
    post_deployment_instructions
    
    success "Deployment completed successfully!"
}

# Run main function
main "$@"
