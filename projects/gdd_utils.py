from bs4 import BeautifulSoup
import re
from .game_models import GDDSection, GDDFeature, GameTask

def extract_features_from_html(html_content):
    """
    Extract features from HTML content of a GDD
    Returns a list of dictionaries with feature information
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    features = []
    
    # Find all feature tables
    feature_tables = soup.find_all('table', class_='feature-table')
    
    for table in feature_tables:
        # Get the section title from the closest h2
        section_header = table.find_previous('h2')
        section_title = section_header.text.strip() if section_header else "Unknown Section"
        section_id = section_header.get('id') if section_header else None
        
        # Extract features from the table
        rows = table.find_all('tr')
        if len(rows) > 0:  # Skip empty tables
            headers = [th.text.strip().lower() for th in rows[0].find_all('th')]
            
            # Check if this is a feature table with the expected columns
            if 'feature' in headers and 'description' in headers:
                feature_idx = headers.index('feature')
                desc_idx = headers.index('description')
                status_idx = headers.index('status') if 'status' in headers else None
                priority_idx = headers.index('priority') if 'priority' in headers else None
                
                # Process each row (skip header)
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) > max(feature_idx, desc_idx):
                        feature = {
                            'section_title': section_title,
                            'section_id': section_id,
                            'feature_name': cells[feature_idx].text.strip(),
                            'description': cells[desc_idx].text.strip(),
                        }
                        
                        # Extract status if available
                        if status_idx is not None and len(cells) > status_idx:
                            status_cell = cells[status_idx]
                            status_span = status_cell.find('span', class_=re.compile('status'))
                            feature['status'] = status_span.text.strip() if status_span else status_cell.text.strip()
                        
                        # Extract priority if available
                        if priority_idx is not None and len(cells) > priority_idx:
                            priority_cell = cells[priority_idx]
                            priority_span = priority_cell.find('span', class_=re.compile('priority'))
                            priority_text = priority_span.text.strip() if priority_span else priority_cell.text.strip()
                            feature['priority'] = priority_text.lower()
                        
                        features.append(feature)
    
    return features

def create_sections_and_features(gdd, html_content):
    """
    Create or update GDD sections and features from HTML content
    """
    features_data = extract_features_from_html(html_content)
    sections_created = {}
    features_created = []
    
    for feature_data in features_data:
        section_title = feature_data['section_title']
        section_id = feature_data['section_id'] or f"section-{len(sections_created) + 1}"
        
        # Create or get section
        if section_id not in sections_created:
            section, created = GDDSection.objects.get_or_create(
                gdd=gdd,
                section_id=section_id,
                defaults={
                    'title': section_title,
                    'order': len(sections_created) + 1
                }
            )
            sections_created[section_id] = section
        else:
            section = sections_created[section_id]
        
        # Create feature
        priority = feature_data.get('priority', 'medium')
        if priority not in [choice[0] for choice in GDDFeature.PRIORITY_CHOICES]:
            priority = 'medium'
            
        feature, created = GDDFeature.objects.get_or_create(
            section=section,
            feature_name=feature_data['feature_name'],
            defaults={
                'description': feature_data['description'],
                'priority': priority
            }
        )
        
        if created:
            features_created.append(feature)
    
    return sections_created, features_created

def convert_feature_to_task(feature, game):
    """
    Convert a GDD feature to a game task
    """
    if feature.task:
        return feature.task
    
    # Determine task type based on section title
    section_title = feature.section.title.lower()
    section_name = feature.section.title  # Original section name with proper capitalization
    task_type = 'other'  # Default
    custom_type = None  # For storing custom type if needed
    
    # Map section title to task type
    if 'design' in section_title or 'gameplay' in section_title or 'mechanic' in section_title:
        task_type = 'design'
    elif 'art' in section_title or 'visual' in section_title or 'graphic' in section_title:
        task_type = 'art'
    elif 'program' in section_title or 'code' in section_title or 'system' in section_title or 'technical' in section_title:
        task_type = 'programming'
    elif 'audio' in section_title or 'sound' in section_title or 'music' in section_title:
        task_type = 'audio'
    elif 'test' in section_title or 'qa' in section_title or 'quality' in section_title:
        task_type = 'testing'
    elif 'story' in section_title or 'narrative' in section_title or 'text' in section_title or 'writing' in section_title:
        task_type = 'writing'
    else:
        # If no standard type matches, use the section name as a custom type
        task_type = 'other'
        custom_type = section_name
    
    # Create a new task
    task = GameTask.objects.create(
        game=feature.section.gdd.game,
        title=feature.feature_name,
        description=feature.description,
        task_type=task_type,
        custom_type=custom_type,  # Set custom_type if it's not None
        status='backlog',  # Using valid status from GameTask.STATUS_CHOICES
        priority=feature.priority,
        gdd_section=feature.section
    )
    
    # Link the task to the feature
    feature.task = task
    feature.save()
    
    return task

def update_gdd_html_with_task_status(gdd):
    """
    Update the HTML content of the GDD with the current task statuses
    """
    if not gdd.html_content:
        return
    
    soup = BeautifulSoup(gdd.html_content, 'html.parser')
    features = GDDFeature.objects.filter(section__gdd=gdd).select_related('task', 'section')
    
    for feature in features:
        if not feature.task:
            continue
            
        # Find the feature in the HTML
        feature_tables = soup.find_all('table', class_='feature-table')
        for table in feature_tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) >= 1 and cells[0].text.strip() == feature.feature_name:
                    # Found the feature, update its status
                    status_cells = [cell for cell in cells if cell.find('span', class_=re.compile('status'))]
                    if status_cells:
                        status_cell = status_cells[0]
                        status_span = status_cell.find('span', class_=re.compile('status'))
                        if status_span:
                            status_span.string = feature.status
                            status_class = f"status {feature.task.status}"
                            status_span['class'] = status_class
                    break
    
    # Update the GDD HTML content
    gdd.html_content = str(soup)
    gdd.save()
    
    return gdd.html_content
