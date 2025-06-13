# R1D3 Company Organization System

A web-based system built with Django to organize and manage your company's:

- **Strategic Vision**: Long-term goals and vision for the company
- **Objectives**: Short and medium-term objectives (OKRs and KPIs)
- **Projects**: Current and planned projects with tracking and resources
- **Resources**: Team structure and resource allocation
- **Documentation**: Processes, guidelines, and best practices

## Technology Stack

- **Backend**: Django (Python web framework)
- **Frontend**: Bootstrap 5 with Django Templates
- **Database**: PostgreSQL (production) / SQLite (development)
- **Deployment**: AWS or similar cloud platform

## Features

- User authentication and role-based permissions
- Dashboard with company KPIs and project status
- Strategic planning tools and goal tracking
- Project management with tasks and milestones
- Resource allocation and team management
- Document repository with version control

## Development Setup

1. Install Python 3.9+ and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Deployment

Instructions for deploying to AWS or other cloud platforms will be added as the project develops.

## Project Structure

- `company_system/` - Main Django project folder
- `core/` - Core functionality and shared components
- `strategy/` - Strategic planning and goal tracking
- `projects/` - Project management functionality
- `resources/` - Resource and team management
- `docs/` - Documentation management
