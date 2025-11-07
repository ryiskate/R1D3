# Text-Based Ownership Implementation Plan

## Overview
Replace User ForeignKeys with text fields + add user profile selection for filtering.

## Solution Architecture

### Part 1: Add Text Fields for Ownership
- Add `created_by_name` and `assigned_to_name` to all task models
- Keep existing ForeignKeys temporarily for backward compatibility

### Part 2: User Profile Selection
Add a simple profile selector so each user can identify themselves:
- Store "current_user_name" in session
- Show a dropdown on first login: "Who are you? [Ricardo] [Partner Name]"
- Use this for filtering "My Tasks"

### Part 3: Dashboard Filtering
Replace:
```python
tasks.filter(assigned_to=request.user)
```

With:
```python
current_user_name = request.session.get('current_user_name')
tasks.filter(assigned_to_name=current_user_name)
```

## Implementation Steps

### Step 1: Add User Profile Middleware
Create a middleware that:
1. Checks if user has selected their name
2. If not, redirect to profile selection page
3. Store selection in session

### Step 2: Database Changes
1. Add text fields to BaseTask model
2. Run migration
3. Copy existing user data to text fields

### Step 3: Update Forms
1. Replace User dropdowns with text field dropdowns
2. Auto-populate created_by_name from session

### Step 4: Update Views
1. Replace `request.user` filters with `request.session.get('current_user_name')`
2. Update all dashboard views
3. Update task creation to use session name

### Step 5: Update Templates
1. Display text fields instead of user objects
2. Update filters to use text fields

## Benefits
✅ Works with shared admin account
✅ Each person identifies themselves once per session
✅ "My Tasks" filtering still works
✅ No user ID conflicts
✅ Perfect for Git sync
✅ Simple to understand and maintain

## Team Member Configuration
Store team members in settings.py:
```python
TEAM_MEMBERS = [
    'Ricardo',
    'Partner Name',
]
```

This makes it easy to add more people later.
