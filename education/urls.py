from django.urls import path
from . import views
from . import debug_views
from . import knowledge_views

app_name = 'education'

urlpatterns = [
    path('', views.EducationDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.EducationDashboardView.as_view(), name='dashboard'),
    path('classes/', views.ClassesView.as_view(), name='classes'),
    path('materials/', views.CourseMaterialsView.as_view(), name='materials'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('tasks/', views.EducationTasksView.as_view(), name='tasks'),  # Using the education app's view
    path('debug-tasks/', debug_views.DebugEducationTasksView.as_view(), name='debug_tasks'),
    path('tasks/newtask/', views.EducationTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.EducationTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.EducationTaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.EducationTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/status-update/', views.EducationTaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/hours-update/', views.EducationTaskHoursUpdateView.as_view(), name='task_hours_update'),
    path('tasks/batch-update/', views.EducationTaskBatchUpdateView.as_view(), name='batch_task_update'),
    
    # Knowledge Base URLs
    path('knowledge/', knowledge_views.KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('knowledge/create/', knowledge_views.KnowledgeArticleCreateView.as_view(), name='knowledge_article_create'),
    path('knowledge/article/<slug:slug>/', knowledge_views.KnowledgeArticleDetailView.as_view(), name='knowledge_article'),
    path('knowledge/article/<slug:slug>/edit/', knowledge_views.KnowledgeArticleUpdateView.as_view(), name='knowledge_article_update'),
    path('knowledge/article/<slug:slug>/delete/', knowledge_views.KnowledgeArticleDeleteView.as_view(), name='knowledge_article_delete'),
    path('knowledge/category/<slug:slug>/', knowledge_views.KnowledgeCategoryView.as_view(), name='knowledge_category'),
    path('knowledge/tag/<slug:slug>/', knowledge_views.KnowledgeTagView.as_view(), name='knowledge_tag'),
    path('knowledge/article/<slug:slug>/upload-media/', knowledge_views.MediaAttachmentUploadView.as_view(), name='media_upload'),
    path('knowledge/media/<int:pk>/delete/', knowledge_views.MediaAttachmentDeleteView.as_view(), name='media_delete'),
    path('knowledge/test-form/', knowledge_views.TestFormView.as_view(), name='knowledge_test_form'),
]
