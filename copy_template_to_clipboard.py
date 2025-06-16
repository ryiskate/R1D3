"""
Script to copy the GDD template content to clipboard for easy pasting into the HTML editor.
"""
import os
import pyperclip  # You may need to install this: pip install pyperclip

def copy_template_to_clipboard():
    try:
        # Read the updated template file
        template_path = os.path.join('static', 'templates', 'gdd_template.html')
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        # Copy to clipboard
        pyperclip.copy(template_content)
        print("GDD template content copied to clipboard!")
        print("Now you can paste it into the HTML editor on the GDD creation page.")
        print("1. Go to http://127.0.0.1:8000/games/2/gdd/create/")
        print("2. Make sure 'Use HTML Editor' is checked")
        print("3. Click the 'Paste from Clipboard' button or use Ctrl+V in the editor")
        print("4. Click 'Save GDD' to create the GDD with the updated template")
        
    except Exception as e:
        print(f"Error copying template: {str(e)}")

if __name__ == "__main__":
    copy_template_to_clipboard()
