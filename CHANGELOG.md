# Changelog

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
