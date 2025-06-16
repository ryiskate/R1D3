from bs4 import BeautifulSoup
import re
from django.forms import formset_factory
from .game_models import GDDSection, GDDFeature, GameTask
from .gdd_structured_form import GDDFeatureFormSet, GDDSubsectionFormSet, STANDARD_GDD_SECTIONS

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


def prepare_structured_gdd_sections(gdd=None):
    """
    Prepare structured GDD sections for the template based on the 13-section industry-standard template.
    If a GDD is provided, it will map existing sections to the standard template.
    Returns a dictionary with section formsets and feature formsets.
    """
    section_formsets = {}
    
    # Map existing sections to standard sections if GDD exists
    existing_sections = {}
    existing_subsections = {}
    existing_features = {}
    
    if gdd:
        # Get all sections for this GDD
        for section in GDDSection.objects.filter(gdd=gdd).order_by('order'):
            existing_sections[section.section_id] = section
            
            # Get features for this section and organize by subsection_id
            section_features = GDDFeature.objects.filter(section=section).order_by('id')
            for feature in section_features:
                if section.section_id not in existing_features:
                    existing_features[section.section_id] = {}
                
                subsection_key = feature.subsection_id if feature.subsection_id else 'main'
                if subsection_key not in existing_features[section.section_id]:
                    existing_features[section.section_id][subsection_key] = []
                
                existing_features[section.section_id][subsection_key].append(feature)
    
    # Prepare formsets for each standard section
    for section in STANDARD_GDD_SECTIONS:
        section_id = section['section_id']
        section_data = {
            'title': section['title'],
            'section_id': section_id,
            'order': section['order'],
            'content': '',
            'description': section.get('description', ''),
            'subsections': []
        }
        
        # If this section exists in the GDD, use its content
        if section_id in existing_sections:
            existing_section = existing_sections[section_id]
            section_data['content'] = existing_section.content
            section_data['id'] = existing_section.id
        
        # Process subsections
        subsections_data = {}
        for i, subsection in enumerate(section.get('subsections', [])):
            subsection_id = subsection.get('subsection_id', f"{section_id}_{i}")
            subsection_data = {
                'title': subsection.get('title', ''),
                'subsection_id': subsection_id,
                'description': subsection.get('description', ''),
                'order': i,
                'content': ''
            }
            
            # Add to section data
            section_data['subsections'].append(subsection_data)
            
            # Store for formset
            subsections_data[subsection_id] = subsection_data['content']
        
        # Create feature formsets - we'll create empty ones here
        # The actual feature formsets will be loaded via AJAX
        feature_formset = GDDFeatureFormSet(prefix=f'feature_{section_id}', 
                                          queryset=GDDFeature.objects.none())
        
        # Store formsets
        section_formsets[section_id] = {
            'section': section_data,
            'feature_formset': feature_formset,
            'subsections': subsections_data
        }
    
    return section_formsets
