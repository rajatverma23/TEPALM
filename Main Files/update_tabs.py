import json

notebook_path = '/Users/vritisharma/Documents/BharatGen_Tools/TEPALM/main_files/Pandulipi_Combined.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def modify_source(source):
    new_source = []
    i = 0
    while i < len(source):
        line = source[i]
        
        # Adjust min-width in the stylesheet from 120px to 150px (+25%)
        if 'min-width: 120px;' in line:
            new_source.append(line.replace('min-width: 120px;', 'min-width: 150px;'))
            
        # Swap tab additions 
        elif 'self.control_tabs.addTab(tab_speech, "Speech & Typing")' in line:
            # We skip this line for now, and inject it after VLM
            pass
            
        elif 'self.control_tabs.addTab(tab_qwen, "VLM based Correction")' in line:
            new_source.append(line)
            # Find the indentation of the line to match it
            indent = len(line) - len(line.lstrip())
            new_source.append(' ' * indent + 'self.control_tabs.addTab(tab_speech, "Speech & Typing")\\n')
            
        else:
            new_source.append(line)
            
        i += 1
        
    return new_source

modified = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        if any('class PDFOCRViewer(QMainWindow):' in line for line in source) and any('QTabBar::tab {' in line for line in source):
            cell['source'] = modify_source(source)
            modified = True
            print("Successfully updated tab layout and widths in UI cell.")
            break

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
        f.write("\n")
    print("Notebook saved successfully.")
else:
    print("Could not find the target cell to modify.")
