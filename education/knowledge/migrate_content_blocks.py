#!/usr/bin/env python
"""
Script to migrate existing knowledge articles with content blocks from session storage to the new JSONField.

Usage:
    docker exec r1d3-web-1 python -m education.knowledge.migrate_content_blocks

This script will:
1. Find all knowledge articles that have content blocks (content field starts with 'Content blocks:')
2. Check if they already have content_blocks data in the JSONField
3. If not, try to find content blocks in the session storage
4. If found, migrate the content blocks to the JSONField
5. If not found, mark the article as needing manual migration
"""

import os
import sys
import json
import logging
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'r1d3.settings')
django.setup()

from django.contrib.sessions.models import Session
from education.knowledge.models import KnowledgeArticle

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_content_blocks():
    """Migrate content blocks from session storage to JSONField"""
    # Find all articles that have content blocks
    articles = KnowledgeArticle.objects.filter(content__startswith='Content blocks:')
    logger.info(f"Found {articles.count()} articles with content blocks")
    
    migrated_count = 0
    already_migrated_count = 0
    failed_count = 0
    
    for article in articles:
        if article.content_blocks:
            logger.info(f"Article {article.id} ({article.title}) already has content blocks in JSONField")
            already_migrated_count += 1
            continue
        
        # Try to find content blocks in session storage
        found_in_session = False
        
        # Get all sessions
        sessions = Session.objects.all()
        for session in sessions:
            session_data = session.get_decoded()
            content_blocks_key = f'article_{article.id}_content_blocks'
            
            if content_blocks_key in session_data:
                content_blocks_data = session_data[content_blocks_key]
                try:
                    content_blocks = json.loads(content_blocks_data)
                    article.content_blocks = content_blocks
                    article.save(update_fields=['content_blocks'])
                    logger.info(f"Migrated content blocks for article {article.id} ({article.title})")
                    migrated_count += 1
                    found_in_session = True
                    break
                except json.JSONDecodeError:
                    logger.error(f"Error parsing content blocks JSON for article {article.id}")
        
        if not found_in_session:
            logger.warning(f"Could not find content blocks in session for article {article.id} ({article.title})")
            failed_count += 1
    
    logger.info(f"Migration complete:")
    logger.info(f"- {migrated_count} articles migrated")
    logger.info(f"- {already_migrated_count} articles already had content blocks in JSONField")
    logger.info(f"- {failed_count} articles could not be migrated (content blocks not found in session)")

if __name__ == '__main__':
    logger.info("Starting content blocks migration")
    migrate_content_blocks()
    logger.info("Content blocks migration completed")
