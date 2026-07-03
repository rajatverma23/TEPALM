import json

notebook_path = '/Users/vritisharma/Documents/BharatGen_Tools/TEPALM/main_files/Pandulipi_Combined.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def modify_source(source):
    new_source = []
    i = 0
    while i < len(source):
        line = source[i]
        
        # Increase min-width in the stylesheet from 150px to 200px to avoid trimming
        if 'min-width: 150px;' in line:
            new_source.append(line.replace('min-width: 150px;', 'padding: 8px 20px;\\n                min-width: 180px;'))
            
        # Group OCR settings and File Controls into one row
        elif 'tab_doc_ocr_layout.addWidget(ocr_group)' in line:
            indent = line[:len(line) - len(line.lstrip())]
            new_source.append(indent + 'ocr_file_layout = QHBoxLayout()\\n')
            new_source.append(indent + 'ocr_file_layout.addWidget(ocr_group)\\n')
            new_source.append(indent + 'tab_doc_ocr_layout.addLayout(ocr_file_layout)\\n')
            
        elif 'tab_doc_ocr_layout.addWidget(file_controls_group)' in line:
            new_source.append(line.replace('tab_doc_ocr_layout.addWidget(file_controls_group)', 'ocr_file_layout.addWidget(file_controls_group)'))
            
        else:
            new_source.append(line)
            
        i += 1
        
    return new_source

modified = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        if any('class PDFOCRViewer(QMainWindow):' in line for line in source):
            cell['source'] = modify_source(source)
            modified = True
            print("Successfully updated UI layout and tab widths.")
            break

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
        f.write("\n")
    print("Notebook saved successfully.")
else:
    print("Could not find the target cell to modify.")
