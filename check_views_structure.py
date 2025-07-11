#!/usr/bin/env python
"""
Script to check the structure of the views.py file and identify any issues with imports or indentation.
"""
import os
import sys
import re

def check_views_structure(file_path):
    """Check the structure of the views.py file and report any issues."""
    print(f"Checking structure of: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for the redirect import
    redirect_imports = [i for i, line in enumerate(lines) if 'from django.shortcuts import redirect' in line]
    print(f"Found {len(redirect_imports)} lines with 'from django.shortcuts import redirect':")
    for i in redirect_imports:
        print(f"  Line {i+1}: {lines[i]}")
    
    # Check for the StrategyMilestoneUpdateView class
    class_pattern = r'class StrategyMilestoneUpdateView\(.*?\):'
    class_matches = list(re.finditer(class_pattern, content))
    
    if not class_matches:
        print("Error: Could not find StrategyMilestoneUpdateView class in the file.")
        return False
    
    print(f"Found StrategyMilestoneUpdateView class at line {content[:class_matches[0].start()].count(chr(10))+1}")
    
    # Find the post method within the class
    class_start = class_matches[0].start()
    class_content = content[class_start:]
    post_pattern = r'def post\(self, request, \*args, \*\*kwargs\):'
    post_matches = list(re.finditer(post_pattern, class_content))
    
    if not post_matches:
        print("Error: Could not find post method in StrategyMilestoneUpdateView class.")
        return False
    
    post_line = content[:class_start].count('\n') + class_content[:post_matches[0].start()].count('\n') + 1
    print(f"Found post method at line {post_line}")
    
    # Check the indentation of the post method
    post_start_idx = class_start + post_matches[0].start()
    post_content_start = content.find('\n', post_start_idx) + 1
    
    # Get the first few lines after the post method definition
    post_lines = content[post_content_start:post_content_start+200].split('\n')
    print("\nFirst few lines after post method definition:")
    for i, line in enumerate(post_lines[:5]):
        print(f"  Line {post_line+i+1}: '{line}'")
    
    # Check for indentation issues
    if post_lines and post_lines[0].strip() and not post_lines[0].startswith(' '):
        print("\nIndentation issue detected: First line after post method definition is not indented.")
    
    # Check for the use of redirect in the post method
    post_end_idx = content.find('def ', post_content_start)
    if post_end_idx == -1:
        post_end_idx = len(content)
    
    post_content = content[post_content_start:post_end_idx]
    redirect_uses = re.findall(r'redirect\(', post_content)
    print(f"\nFound {len(redirect_uses)} uses of redirect() in the post method.")
    
    return True

def main():
    """Main function to run the script."""
    # Check if a file path was provided as an argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default path for local development
        file_path = os.path.join('strategy', 'views.py')
        
        # Check if we're in the project root
        if not os.path.exists(file_path):
            # Try to find the file in the current directory structure
            for root, _, files in os.walk('.'):
                if 'views.py' in files and 'strategy' in root:
                    potential_path = os.path.join(root, 'views.py')
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        break
    
    # Ensure the file path is absolute
    file_path = os.path.abspath(file_path)
    
    print(f"Processing strategy views file at: {file_path}")
    
    if check_views_structure(file_path):
        print("\nStructure check completed.")
        print("Please review the output above for any issues with imports or indentation.")
    else:
        print("\nFailed to check structure.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
