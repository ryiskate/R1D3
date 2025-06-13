from django.contrib import admin
from .game_models import (
    GameProject, GameDesignDocument, GameAsset, GameMilestone, 
    GameTask, GameBuild, PlaytestSession, PlaytestFeedback, GameBug
)

@admin.register(GameProject)
class GameProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'genre', 'lead_developer', 'start_date', 'target_release_date')
    list_filter = ('status', 'genre', 'platforms')
    search_fields = ('title', 'description', 'tagline')
    date_hierarchy = 'start_date'
    filter_horizontal = ('team_members',)


@admin.register(GameDesignDocument)
class GameDesignDocumentAdmin(admin.ModelAdmin):
    list_display = ('game', 'created_at', 'updated_at')
    search_fields = ('game__title', 'high_concept')


@admin.register(GameAsset)
class GameAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'asset_type', 'status', 'created_by', 'created_at')
    list_filter = ('asset_type', 'status')
    search_fields = ('name', 'description', 'game__title')


@admin.register(GameMilestone)
class GameMilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'due_date', 'is_completed', 'completion_date')
    list_filter = ('is_completed',)
    search_fields = ('title', 'description', 'game__title')


@admin.register(GameTask)
class GameTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'task_type', 'status', 'priority', 'assigned_to', 'due_date')
    list_filter = ('status', 'priority', 'task_type')
    search_fields = ('title', 'description', 'game__title')


@admin.register(GameBuild)
class GameBuildAdmin(admin.ModelAdmin):
    list_display = ('game', 'version_number', 'version_type', 'build_date', 'platform', 'is_public')
    list_filter = ('version_type', 'platform', 'is_public')
    search_fields = ('game__title', 'version_number', 'notes')


@admin.register(PlaytestSession)
class PlaytestSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'build', 'date', 'location', 'is_remote', 'participants_count')
    list_filter = ('is_remote',)
    search_fields = ('title', 'game__title', 'objectives')


@admin.register(PlaytestFeedback)
class PlaytestFeedbackAdmin(admin.ModelAdmin):
    list_display = ('session', 'tester_name', 'tester_email', 'overall_experience', 'created_at')
    list_filter = ('overall_experience',)
    search_fields = ('tester_name', 'tester_email', 'session__title')


@admin.register(GameBug)
class GameBugAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'severity', 'status', 'assigned_to', 'created_at')
    list_filter = ('severity', 'status')
    search_fields = ('title', 'description', 'game__title')
