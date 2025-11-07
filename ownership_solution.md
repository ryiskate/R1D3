# Task & Project Ownership Solution for Git-Based Sync

## Current Problem

Your models have these User ForeignKey fields:
- **Tasks**: `created_by`, `assigned_to`
- **Projects**: Risk `owner`
- **Base Task Models**: All inherit `created_by` and `assigned_to`

With Git sync and 2 users sharing the same database:
- ❌ User IDs will conflict
- ❌ "Assigned to User 1" might be different people on each machine
- ❌ Can't track who actually did the work

## Proposed Solutions

### **Option 1: Text-Based Ownership (RECOMMENDED)**

Replace User ForeignKeys with simple text fields for names.

**Pros:**
✅ No user ID conflicts
✅ Works perfectly with Git sync
✅ Simple to implement
✅ Both users can see who owns what
✅ No database conflicts

**Cons:**
❌ Lose Django's built-in user filtering
❌ No automatic user validation
❌ Manual entry (but can use dropdowns)

**Implementation:**
```python
# Instead of:
assigned_to = models.ForeignKey(User, ...)

# Use:
assigned_to_name = models.CharField(max_length=100, blank=True)
created_by_name = models.CharField(max_length=100, blank=True)
```

---

### **Option 2: Keep User ForeignKeys + Username Mapping**

Keep the current structure but ensure both users have the same User IDs.

**Setup:**
1. Create 2 users with specific IDs on both machines:
   - User ID 1: "Ricardo"
   - User ID 2: "Partner Name"
2. Both machines must have identical user records
3. Each person logs in as themselves

**Pros:**
✅ Keeps current Django structure
✅ Proper user authentication
✅ Can use Django's user filtering

**Cons:**
❌ Complex setup - must manually ensure user IDs match
❌ If users get out of sync, everything breaks
❌ Can't easily add more users later
❌ Password sync issues (see previous discussion)

---

### **Option 3: Hybrid - Keep Auth, Add Text Fields**

Keep User ForeignKeys for authentication, but add text fields for display.

**Implementation:**
```python
class BaseTask(models.Model):
    # Keep for authentication/permissions
    created_by = models.ForeignKey(User, ...)
    assigned_to = models.ForeignKey(User, ...)
    
    # Add for display/tracking
    created_by_name = models.CharField(max_length=100, blank=True)
    assigned_to_name = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-populate names from user objects if available
        if self.created_by and not self.created_by_name:
            self.created_by_name = self.created_by.username
        if self.assigned_to and not self.assigned_to_name:
            self.assigned_to_name = self.assigned_to.username
        super().save(*args, **kwargs)
```

**Pros:**
✅ Keeps Django authentication
✅ Text fields survive Git sync
✅ Backward compatible

**Cons:**
❌ Redundant data
❌ More complex
❌ Still has user ID issues

---

## Recommended Implementation Plan

### **Go with Option 1: Text-Based Ownership**

This is the cleanest solution for your 2-person local Git workflow.

### Changes Needed:

1. **Migration to add text fields:**
   - `created_by_name` (CharField)
   - `assigned_to_name` (CharField)
   - `owner_name` (CharField for risks)

2. **Update forms to use dropdowns:**
   ```python
   TEAM_MEMBERS = [
       ('', '-- Unassigned --'),
       ('Ricardo', 'Ricardo'),
       ('Partner Name', 'Partner Name'),
   ]
   
   assigned_to_name = forms.ChoiceField(
       choices=TEAM_MEMBERS,
       required=False
   )
   ```

3. **Data migration:**
   - Copy existing user data to text fields
   - Keep old ForeignKey fields for now (don't break existing data)

4. **Update templates:**
   - Display `assigned_to_name` instead of `assigned_to.username`
   - Filter by text field instead of user object

### Quick Start Script:

Would you like me to create:
1. ✅ Migration files to add the new text fields
2. ✅ Data migration script to copy existing user data
3. ✅ Updated forms with dropdown selections
4. ✅ Updated templates to use text fields

This way you can:
- Keep your Git sync workflow
- Track ownership clearly
- No user ID conflicts
- Easy to understand who owns what
