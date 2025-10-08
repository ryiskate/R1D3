#!/usr/bin/env python
"""
Script to fix Django Site configuration for R1D3 on PythonAnywhere.
This script:
1. Creates or updates the Site object in the database
2. Ensures SITE_ID matches the database
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.sites.models import Site
from django.conf import settings

def fix_django_site():
    """Fix Django Site configuration."""
    print("=== Fixing Django Site Configuration ===\n")
    
    # Get the SITE_ID from settings
    site_id = getattr(settings, 'SITE_ID', 1)
    print(f"SITE_ID in settings: {site_id}")
    
    # Check if Site with this ID exists
    try:
        site = Site.objects.get(pk=site_id)
        print(f"Found existing Site: {site.domain} - {site.name}")
        
        # Update the site with correct domain
        site.domain = 'r1d3.pythonanywhere.com'
        site.name = 'R1D3'
        site.save()
        print(f"✓ Updated Site to: {site.domain} - {site.name}")
        
    except Site.DoesNotExist:
        print(f"Site with ID {site_id} does not exist. Creating it...")
        
        # Create the site
        site = Site.objects.create(
            pk=site_id,
            domain='r1d3.pythonanywhere.com',
            name='R1D3'
        )
        print(f"✓ Created Site: {site.domain} - {site.name}")
    
    # List all sites
    print("\nAll sites in database:")
    for s in Site.objects.all():
        print(f"  ID: {s.pk}, Domain: {s.domain}, Name: {s.name}")
    
    print("\n=== Site Configuration Fixed ===")
    print("Restart your web app with:")
    print("  touch /var/www/R1D3_pythonanywhere_com_wsgi.py")

if __name__ == "__main__":
    fix_django_site()
