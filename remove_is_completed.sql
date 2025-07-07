-- SQL script to remove is_completed field from GameMilestone model
-- This script bypasses Django's migration system to avoid dependency issues

-- Remove the is_completed column from the projects_gamemilestone table
ALTER TABLE "projects_gamemilestone" DROP COLUMN "is_completed";

-- Update Django's migration history to mark our migration as applied
-- This prevents Django from trying to run this migration again
INSERT INTO django_migrations (app, name, applied)
VALUES ('projects', '0003_remove_is_completed_from_milestone', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
