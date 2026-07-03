import json

notebook_path = '/Users/vritisharma/Documents/BharatGen_Tools/TEPALM/main_files/Pandulipi_Combined.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def modify_source(source):
    new_source = []
    i = 0
    in_tab_creation = False
    
    while i < len(source):
        line = source[i]
        
        # Replace the separate tab creations with a single one
        if 'tab_doc = QWidget()' in line:
            new_source.append(line.replace('tab_doc = QWidget()', 'tab_doc_ocr = QWidget()'))
        elif 'tab_doc_layout = QVBoxLayout()' in line:
            new_source.append(line.replace('tab_doc_layout = QVBoxLayout()', 'tab_doc_ocr_layout = QVBoxLayout()'))
        elif 'tab_doc.setLayout(tab_doc_layout)' in line:
            new_source.append(line.replace('tab_doc.setLayout(tab_doc_layout)', 'tab_doc_ocr.setLayout(tab_doc_ocr_layout)'))
        elif 'self.control_tabs.addTab(tab_doc, "Document & Vision")' in line:
            new_source.append(line.replace('self.control_tabs.addTab(tab_doc, "Document & Vision")', 'self.control_tabs.addTab(tab_doc_ocr, "Document OCR")'))
        
        # Remove Tab 2 creation lines
        elif 'tab_ocr = QWidget()' in line or \
             'tab_ocr_layout = QVBoxLayout()' in line or \
             'tab_ocr.setLayout(tab_ocr_layout)' in line or \
             'self.control_tabs.addTab(tab_ocr, "OCR & Spell Check")' in line or \
             '# Tab 2: OCR & Proofreading' in line:
            pass # Skip these lines completely
            
        # Replace occurrences of tab_doc_layout and tab_ocr_layout
        elif 'tab_doc_layout.add' in line or 'tab_ocr_layout.add' in line:
            modified_line = line.replace('tab_doc_layout', 'tab_doc_ocr_layout').replace('tab_ocr_layout', 'tab_doc_ocr_layout')
            new_source.append(modified_line)
            
        # Add the stylesheet after self.setCentralWidget(main_widget)
        elif 'self.setCentralWidget(main_widget)' in line:
            new_source.append(line)
            # Add academic presentation stylesheet
            stylesheet = """        # Academic Presentation Stylesheet
        self.setStyleSheet('''
            QMainWindow {
                background-color: #f4f6f8;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #d1d9e6;
                border-radius: 6px;
                margin-top: 15px;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            QPushButton {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px 12px;
                color: #2c3e50;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e0e6ed;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #d1d8e0;
            }
            QPushButton:disabled {
                background-color: #f9f9f9;
                color: #a0a0a0;
                border: 1px solid #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #d1d9e6;
                background-color: #ffffff;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-bottom-color: #d1d9e6;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 15px;
                min-width: 120px;
                font-weight: bold;
                color: #34495e;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-color: #d1d9e6;
                border-bottom-color: transparent;
                color: #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background: #e4e9ed;
            }
            QLabel {
                color: #34495e;
            }
            QCheckBox {
                color: #34495e;
                font-weight: 500;
            }
        ''')\\n"""
            new_source.append(stylesheet)
            
        else:
            new_source.append(line)
        i += 1
            
    return new_source

modified = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        is_ui_cell = any('class PDFOCRViewer(QMainWindow):' in line for line in source)
        if is_ui_cell:
            cell['source'] = modify_source(source)
            modified = True
            print("Successfully modified PDFOCRViewer initialization cell.")
            break

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
        f.write("\n")
    print("Notebook saved successfully.")
else:
    print("Could not find the target cell to modify.")
