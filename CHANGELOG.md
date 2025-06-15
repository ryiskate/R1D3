# Changelog

## 2025-06-15: Add Game Status Quick Change Feature

### Added
- Added `GameStatusUpdateView` to enable quick status changes directly from the game detail page
- Added status change dropdown in the game detail page for staff members
- Added color-coded status badges for better visual indication of game status

### Files Modified
- Created new file: `projects/game_status_view.py`
- Updated `projects/game_urls.py` to add the status update URL
- Updated `projects/game_views.py` to include status choices in the context
- Updated `templates/projects/game_detail.html` to add the status change dropdown

## 2025-06-15: Fix Game Project Edit Functionality

### Added
- Added `GameProjectUpdateView` class to enable editing of existing game projects
- Added URL pattern for game project update functionality

### Fixed
- Fixed the "Edit Game" button in game detail page to correctly link to the update view

### Files Modified
- `projects/game_views.py`
- `projects/game_urls.py`
- `templates/projects/game_detail.html`

## 2025-06-15: Fix Tasks Not Showing on Games Page

### Added
- Added user tasks display to the games list page
- Added `get_context_data` method to `GameProjectListView` to include user tasks in the context

### Changed
- Updated `game_list.html` template to display user tasks in a table format
- Tasks are now filtered by user assignment and active statuses

### Files Modified
- `projects/game_views.py`
- `templates/projects/game_list.html`

## 2025-06-15: Add Custom Thumbnail Field to GameAsset Model

### Added
- Added `thumbnail` ImageField to GameAsset model in `projects/game_models.py`
- Created migration `0006_gameasset_thumbnail.py` for the new field
- Added thumbnail field to GameAssetForm in `projects/game_forms.py`
- Added thumbnail upload section to asset form template
- Added thumbnail display to asset list and detail templates

### Changed
- Updated asset list template to prioritize custom thumbnails
- Updated asset detail template to show thumbnails when available
- Removed status display from asset list for cleaner UI

### Files Modified
- `projects/game_models.py`
- `projects/game_forms.py`
- `projects/migrations/0006_gameasset_thumbnail.py` (new file)
- `templates/projects/asset_form.html`
- `templates/projects/asset_list.html`
- `templates/projects/asset_detail.html`
