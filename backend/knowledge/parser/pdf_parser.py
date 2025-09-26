import fitz
import re

def extract_meaningful_content(text):
    """
    Extract meaningful content by removing navigation elements and repetitive content
    """
    # Remove excessive repetitive navigation elements
    text = re.sub(r'(\n\n\n)+', '\n\n', text)

    # Remove lines that are just whitespace or single characters
    lines = text.split('\n')
    meaningful_lines = []

    for line in lines:
        stripped = line.strip()
        # Keep lines that have meaningful content (more than just single chars or common nav elements)
        if len(stripped) > 2 and not re.match(r'^[\s\n\t\xa0]*$', stripped):
            meaningful_lines.append(stripped)

    return '\n'.join(meaningful_lines)

def load_doc(path):
    if str(path).lower().endswith('.pdf'):
        try:
            with fitz.open(str(path)) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
                return extract_meaningful_content(text)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return ""
        
    else:
        print(f"Unsupported file format: {path}")
        return ""
    


if __name__ == "__main__":

    path = input("enter a file path")
    text = load_doc(path)
    print(text)

