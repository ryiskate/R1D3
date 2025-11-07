# Hierarchical Task System - Implementation Guide

## 🎯 Overview

The R1D3 system now supports a 3-level hierarchical task structure:

```
Epic (Story-level)
  └── Task (Feature-level)
      └── Subtask (Implementation-level)
```

## 📊 Structure

### Level 1: Epic
- **Purpose**: Large stories or features that span multiple tasks
- **Company Section**: Each epic belongs to a specific department (Games, Education, etc.)
- **Progress Tracking**: Automatically calculates completion based on task status
- **Fields**:
  - Title, Description
  - Company Section (Games, Education, Social Media, etc.)
  - Status (Planning, In Progress, On Hold, Completed, Cancelled)
  - Priority (Low, Medium, High, Critical)
  - Owner Name (text-based)
  - Start Date, Target Date, Completed Date
  - Tags

### Level 2: Task
- **Purpose**: Individual features or work items within an epic
- **Epic Relationship**: Links to parent epic
- **Subtasks**: Can have multiple subtasks
- **Fields**: All BaseTask fields plus:
  - `task_level = 'task'`
  - `epic` (ForeignKey to Epic)
  - `parent_task = None`

### Level 3: Subtask
- **Purpose**: Specific implementation steps for a task
- **Parent Relationship**: Links to parent task
- **Fields**: All BaseTask fields plus:
  - `task_level = 'subtask'`
  - `parent_task` (ForeignKey to parent Task)
  - `epic = None` (inherited from parent)

## 🔄 Workflow Example

### Creating a Game Character

```python
# 1. Create Epic
epic = Epic.objects.create(
    title="Create Main Character",
    company_section="games",
    status="in_progress",
    priority="high",
    owner_name="Ricardo"
)

# 2. Create Tasks under Epic
backstory_task = GameDevelopmentTask.objects.create(
    title="Character Backstory",
    task_level="task",
    epic=epic,
    assigned_to_name="Ricardo",
    status="in_progress"
)

design_task = GameDevelopmentTask.objects.create(
    title="Character Design",
    task_level="task",
    epic=epic,
    assigned_to_name="Partner",
    status="to_do"
)

# 3. Create Subtasks under Tasks
GameDevelopmentTask.objects.create(
    title="Write childhood history",
    task_level="subtask",
    parent_task=backstory_task,
    assigned_to_name="Ricardo",
    status="done"
)

GameDevelopmentTask.objects.create(
    title="Define motivations",
    task_level="subtask",
    parent_task=backstory_task,
    assigned_to_name="Ricardo",
    status="in_progress"
)

GameDevelopmentTask.objects.create(
    title="Concept art",
    task_level="subtask",
    parent_task=design_task,
    assigned_to_name="Partner",
    status="to_do"
)
```

## 📈 Progress Tracking

### Epic Progress
```python
epic.get_progress()  # Returns 0-100 based on completed tasks
epic.get_task_count()  # Total number of tasks
epic.get_subtask_count()  # Total number of subtasks across all tasks
```

### Task Progress
```python
task.get_subtask_count()  # Number of subtasks
task.get_completed_subtask_count()  # Number of completed subtasks
task.get_subtask_progress()  # Percentage (0-100)
task.get_hierarchy_display()  # "Epic → Task → Subtask"
```

## 🎨 Display Examples

### Epic Card
```
┌─────────────────────────────────────┐
│ 🎮 Create Main Character            │
│ Game Development                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Progress: 45% (5/11 tasks done)     │
│ 11 Tasks • 23 Subtasks              │
│ Owner: Ricardo                      │
│ Target: Dec 15, 2025                │
└─────────────────────────────────────┘
```

### Task List View
```
Epic: Create Main Character
  ├── ✅ Character Backstory (3/3 subtasks)
  │   ├── ✅ Write childhood history
  │   ├── ✅ Define motivations
  │   └── ✅ Create family tree
  ├── 🔄 Character Design (1/3 subtasks)
  │   ├── ✅ Concept art
  │   ├── ⏳ 3D model
  │   └── ⏳ Animations
  └── ⏳ Character Abilities (0/2 subtasks)
      ├── ⏳ Design skill tree
      └── ⏳ Balance stats
```

## 🔧 Helper Methods

### Epic Model
- `get_progress()` - Calculate completion percentage
- `get_task_count()` - Count tasks
- `get_subtask_count()` - Count all subtasks
- `__str__()` - Display as "Section: Title"

### BaseTask Model
- `get_subtask_count()` - Count direct subtasks
- `get_completed_subtask_count()` - Count completed subtasks
- `get_subtask_progress()` - Subtask completion percentage
- `is_task_level()` - Check if task level
- `is_subtask_level()` - Check if subtask level
- `get_hierarchy_display()` - Full path display

## 📝 Next Steps

1. ✅ Models created
2. ⏳ Create migrations
3. ⏳ Update forms (Epic form, Task form with epic selector, Subtask form)
4. ⏳ Create Epic management views (list, create, update, detail)
5. ⏳ Update task views to support hierarchy
6. ⏳ Create epic dashboard with progress visualization
7. ⏳ Update templates to show hierarchy
8. ⏳ Add filtering by epic
9. ⏳ Add drag-and-drop for task organization

## 🎯 Benefits

1. **Better Organization**: Group related work logically
2. **Progress Visibility**: See epic and task completion at a glance
3. **Team Coordination**: Assign tasks and subtasks to different team members
4. **Agile Workflow**: Matches modern project management practices
5. **Flexible Structure**: Can use epics, standalone tasks, or full hierarchy
6. **Git-Friendly**: All ownership is text-based for easy syncing
