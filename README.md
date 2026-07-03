# TEPALM — PANDULIPI

**PANDULIPI** (पाण्डुलिपि, "manuscript") is a PyQt5 desktop application for annotating,
transcribing, and spell-checking scanned Devanagari/Sanskrit manuscripts. It combines
OCR, image restoration, VLM-assisted correction, and dictionary-based spell checking
in a single PDF/image viewer and editor.

## Repository Layout

```
TEPALM/
├── Main Files/     # Application source (notebooks, Python modules, config, dictionaries)
├── Dataset/        # Sample manuscript scans grouped by OCR-difficulty category
└── README.md
```

## Main Files

### Application notebooks
The app is built as Jupyter notebooks containing the full PyQt5 UI (class `PDFOCRViewer`
plus supporting workers/dialogs). Each is a self-contained snapshot of the tool at a
different stage of development:

| Notebook | Description |
|---|---|
| `Pandulipi_Combined_latest.ipynb` | Latest full build — merges OCR, spell check, VQA/Qwen correction, and FoundIR restoration. Also includes a separate FastAPI server cell for serving Qwen3-VL. |
| `Pandulipi_Combined_backup.ipynb` | Backup snapshot of the combined build. |
| `Pandulipi_Spell_Check.ipynb` | Standalone build focused on OCR + dictionary-based spell checking. |
| `Pandulipi_VQA.ipynb` | Standalone build focused on Akshara (character) selection, VQA, and image binarization. |

Core features implemented across the app (`PDFOCRViewer` and helpers):
- PDF/image loading and paging, zoom, and region selection (`PDFViewLabel`)
- OCR via Tesseract (custom `tessdata` path support) and Google Cloud Vision, with
  side-by-side comparison of engine outputs
- Image restoration/denoising via a FoundIR model server (`FoundIRClient`)
- Image similarity search for reusing corrected akshara crops (perceptual hashing / KD-tree)
- Manuscript line segmentation, editing, and persistence (`Line_Segments/*.json`)
- Speech-to-text dictation for transcription (`SpeechRecognitionWorker`)
- Qwen3-VL-based vision-language correction/analysis of selected regions (`QwenVLClient`)
- Dictionary-backed spell checking with 4-tier validation and color-coded highlighting
- Trie + Levenshtein-based word auto-suggestions while typing
- In-app feedback submission emailed to the maintainers

### Supporting Python modules
| File | Purpose |
|---|---|
| `spell_check_module_V.py` | `DictionaryManager` (loads/queries main, gbook, pwords, cpair dictionaries) and `SpellChecker`/`SpellCheckHighlighter` for real-time syntax highlighting of valid, domain, corrected, partial, and incorrect words. |
| `word_suggestion_module.py` | Trie-based `WordSuggestionEngine` with Levenshtein fuzzy fallback, coordinated by `SuggestionManager`. |
| `word_suggestion_widget.py` | PyQt5 popup widget and `QTextEdit` integration (auto-complete, `Ctrl+Space` / `Ctrl+Shift+S` shortcuts) for the suggestion engine. |
| `feedback_module_V.py` | In-app feedback dialog that emails bug reports/feature requests (with system/OCR context) via SMTP. |
| `modify_notebook.py`, `update_tabs.py`, `update_tabs_2.py` | One-off scripts used to programmatically patch the `PDFOCRViewer` notebook cell (merging tabs, adjusting the Qt stylesheet, tab widths/layout). Not needed to run the app. |

### Configuration
| File | Purpose |
|---|---|
| `ocr_config.json` | Tesseract settings — `tessdata_path`, OCR `language` (default `san`), page segmentation mode, and auto-OCR toggle. |
| `email_config.json` | SMTP settings used by the feedback module (server, port, sender/recipient, credentials). |
| `pandulipi-482118.json` | Google Cloud service account key used for the Google Vision OCR integration (git-ignored; not committed). |

> ⚠️ **Security note:** `email_config.json` currently contains a live sender address and
> app password and is tracked in git. Rotate that app password and stop tracking the
> file (move credentials to an untracked/local config or environment variables), the
> same way `pandulipi-482118.json` is already excluded via `.gitignore`.

### Dictionaries (`Main Files/Dictionaries/`)
Sample Devanagari dictionaries used by the spell checker, tailored to Ramayana-related
manuscript work (see `Dictionary_Usage.md` for the full guide):

| File | Role |
|---|---|
| `main_dict.txt` | General Sanskrit/Ramayana vocabulary. |
| `gbook.txt` | Large domain-specific term list (manuscript/Ramayana-specific vocabulary). |
| `pwords.txt` | Project-specific words, grown via the app's "Add to Dictionary" action. |
| `cpair.json` | Common OCR error → correction pairs (incorrect → correct Devanagari spelling). |

Lookup priority: `gbook` → `pwords` → `cpair` → `main`, each rendered with a distinct
highlight color in the editor.

### Line segments (`Main Files/Line_Segments/`)
Per-page line segmentation data (bounding boxes) saved by the app for sample documents,
enabling line-level editing/redetection without recomputing segmentation each run.

## Dataset

`Dataset/` contains sample scanned manuscript pages grouped by the OCR challenge they
represent, each with a source PDF and corresponding raw-OCR text extract(s):

| Category | Contents | Challenge illustrated |
|---|---|---|
| `Difficult/` | `Namanighantu.pdf`, `page_3.txt` | Dense/complex Devanagari layout that is hard to OCR accurately. |
| `Eroded/` | `NavtatvaBhasha.pdf`, `page_1.txt` | Physically degraded/eroded manuscript pages with faded or damaged text. |
| `Commentary/` | `Hanuman_Chalisa.pdf`, `Hanuman_Chalisa_Commentary_Hindi.pdf/.txt`, `page_4.txt` | Text interleaved with commentary/annotations. |
| `Multi-OCR/` | `candana_sasthi_vrata_katha.pdf`, `page_1.txt` | Pages intended for comparison across multiple OCR engines. |
| `Clutter/` | `madanastaka.pdf`, `page_1.txt` | Pages with visual clutter (marginalia, decorations, noise) around the main text. |

These samples are used to test and demonstrate the OCR, restoration, and spell-checking
pipeline against realistic manuscript conditions.

## Setup

The app depends on: `PyQt5`, `PyMuPDF (fitz)`, `opencv-python`, `numpy`, `scipy`, `Pillow`,
`google-cloud-vision`, `requests`, `SpeechRecognition`, and (for the bundled Qwen3-VL
server cell) `fastapi`, `torch`, `transformers`.

1. Install Tesseract OCR and set `tessdata_path`/`language` in `ocr_config.json`.
2. Provide a Google Cloud Vision service account key (referenced by the notebook) for
   Google Vision OCR.
3. Configure `email_config.json` with your own SMTP credentials for the feedback feature
   (see the security note above).
4. Open the desired notebook under `Main Files/` (start with
   `Pandulipi_Combined_latest.ipynb`) and run all cells to launch the PyQt5 app.
