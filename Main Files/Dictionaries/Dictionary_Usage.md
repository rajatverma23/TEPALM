# Ramayana Manuscript Dictionary Files - Usage Guide

## 📁 File Overview

This package contains sample dictionary files for PANDULIPI spell checking, specifically tailored for **Ramayana manuscript** transcription work.

### Files Included:

1. **main_dict.txt** - Main Sanskrit/Ramayana vocabulary (~280 words)
2. **gbook.txt** - Domain-specific Ramayana manuscript terms (~150 words)
3. **pwords.txt** - Project-specific words (template with examples)
4. **cpair.json** - Common OCR error corrections (~80 pairs)

---

## 🚀 Installation

### Step 1: Copy files to Dictionaries folder

```bash
# In your PANDULIPI project directory
mkdir -p Dictionaries
cp sample_main_dict.txt Dictionaries/main_dict.txt
cp sample_gbook.txt Dictionaries/gbook.txt
cp sample_pwords.txt Dictionaries/pwords.txt
cp sample_cpair.json Dictionaries/cpair.json
```

### Step 2: Verify installation

When you run PANDULIPI, you should see:
```
✓ Loaded dictionaries:
  Main: 280+ words
  GBook: 150+ words
  PWords: 30+ words
  Correction pairs: 80+ pairs
  Format: Devanagari
```

---

## 📚 Dictionary Hierarchy

The spell checker uses this priority order:

1. **gbook** (Domain-specific) - Gray color
2. **pwords** (Project-specific) - Blue color
3. **cpair** (Corrections) - Purple color + underline
4. **main** (General dictionary) - Green color

---

## 📖 Dictionary Descriptions

### 1. main_dict.txt (General Sanskrit)

**Contains:**
- Common Sanskrit words (धर्म, कर्म, योग, etc.)
- Ramayana main characters (राम, सीता, हनुमान, रावण, etc.)
- Places (अयोध्या, मिथिला, लंका, etc.)
- Common nouns, verbs, adjectives
- Numbers, pronouns, particles
- Nature, body parts, abstract concepts

**When to add words:**
- General Sanskrit vocabulary
- Character names appearing in multiple texts
- Universal Sanskrit grammar particles

**Color:** Green (valid word)

---

### 2. gbook.txt (Domain-specific)

**Contains:**
- Ramayana-specific terminology (काण्ड, सर्ग)
- Seven Kandas (बालकाण्ड, अयोध्याकाण्ड, etc.)
- Divine weapons (ब्रह्मास्त्र, पाशुपतास्त्र)
- Ramayana-specific locations (अशोकवाटिका, ऋष्यमूक)
- Minor characters unique to Ramayana
- Manuscript terminology (श्लोक, पाठान्तर, टीका)

**When to add words:**
- Terms specific to Ramayana manuscripts
- Specialized vocabulary from scholarly editions
- Technical manuscript terms

**Color:** Gray (domain-specific)

---

### 3. pwords.txt (Project-specific)

**Contains:**
- Your manuscript's specific spelling variants
- Scribal conventions unique to your manuscript
- Regional variations
- Frequently occurring phrases
- Manuscript-specific annotations

**When to add words:**
- Words OCR frequently recognizes in YOUR manuscript
- Scribal spelling preferences
- Unique variants not in other dictionaries
- Use "Add to Dictionary" button in PANDULIPI

**Color:** Blue (project-specific)

**💡 This is YOUR working dictionary - customize it!**

---

### 4. cpair.json (OCR Corrections)

**Contains:**
- Common OCR misrecognitions
- Frequent spelling mistakes
- Visually similar character confusions
- Anusvara/Visarga errors (ं/ः)
- Incorrect visarga placements

**Format:**
```json
{
  "incorrect_word": "correct_word",
  "रावन": "रावण",
  "हनुमान": "हनुमान"
}
```

**When to add pairs:**
- When you notice OCR consistently makes same mistake
- When you correct the same error multiple times
- Character similarity issues (ण/न, व/ब, etc.)

**Color:** Purple + Underline (correction available)

---

## 🎨 Color Coding Reference

| Status | Color | Meaning |
|--------|-------|---------|
| Green | Valid | Word in main dictionary |
| Gray | Domain | Word in gbook (Ramayana-specific) |
| Blue | Project | Word in pwords (your manuscript) |
| Purple + Underline | Correction | Correction pair available |
| Cyan | Frequent | Word appears 5+ times (likely valid) |
| Dark Cyan | Compound | Recognized compound word |
| Orange + Italic | ASCII | Mixed script detected |
| Red + Underline | Unknown | Not in any dictionary |

### Partial Matches:
- **Solid color** (Green/Gray/Blue): Word fully covered by subwords from same dictionary
- **Light yellow background**: Mixed sources or incomplete coverage
  - Green highlights: Subwords from main dict
  - Gray highlights: Subwords from gbook
  - Blue highlights: Subwords from pwords
  - Red highlights: Unmatched parts

---

## 🔧 Customization Tips

### Expanding main_dict.txt

Add common words you encounter:
```bash
# Append to main_dict.txt
echo "नमस्ते" >> Dictionaries/main_dict.txt
echo "वन्दे" >> Dictionaries/main_dict.txt
echo "मातरम्" >> Dictionaries/main_dict.txt
```

### Adding to gbook.txt during work

When you find Ramayana-specific terms:
```bash
echo "सेतुबन्धन" >> Dictionaries/gbook.txt
echo "रामेश्वरम्" >> Dictionaries/gbook.txt
```

### Using pwords.txt effectively

1. Start with empty/minimal pwords.txt
2. During transcription, use "Add to Dictionary" button
3. PANDULIPI automatically appends to pwords.txt
4. Review periodically and move common words to main_dict.txt

### Updating cpair.json

Manual method:
```json
{
  "_comment": "Correction pairs: incorrect → correct (Devanagari)",
  "_format": "devanagari",
  
  "रामचंद्र": "रामचन्द्र",
  "YOUR_OCR_ERROR": "CORRECT_WORD"
}
```

**Important:** Don't add words starting with underscore (_) - they're metadata!

---

## 📊 Statistics and Monitoring

View dictionary stats in PANDULIPI:
- Click "Dictionary Stats" button
- Shows word counts for each dictionary
- Total vocabulary size
- Format confirmation (Devanagari)

---

## 🎯 Workflow Recommendations

### Phase 1: Initial Setup
1. Use provided sample dictionaries as-is
2. Start transcribing your manuscript
3. Note frequently appearing unknown words (red)

### Phase 2: Customization
1. Add manuscript-specific words to pwords.txt
2. Add OCR correction pairs to cpair.json
3. Review frequency of cyan words (appears 5+ times)

### Phase 3: Optimization
1. Move stable pwords.txt entries to main_dict.txt
2. Clean up duplicate entries
3. Refine cpair.json with actual OCR patterns

### Phase 4: Sharing
1. Export your customized dictionaries
2. Share with collaborators working on similar manuscripts
3. Contribute to main_dict.txt for community benefit

---

## 🔍 Example: Common OCR Errors

### Visually Similar Characters
```
ण ↔ न   (dental vs retroflex)
व ↔ ब   (va vs ba)
ष ↔ स   (retroflex vs dental s)
ा ↔ ो   (aa vs o matra)
```

### Anusvara/Visarga Confusion
```
ं ↔ ः   (anusvara vs visarga)
रामं → राम (incorrect visarga as anusvara)
धर्मः → धर्म (visarga vs nothing)
```

### Common Spelling Variants
```
रामायन → रामायण (missing anusvara)
हनुमान → हनुमान (already correct but OCR might vary)
लङ्का → लंका (chandrabindu vs anusvara)
```

Add these to cpair.json as you discover them!

---

## 🐛 Troubleshooting

### "No words loaded"
- Check file encoding is UTF-8
- Ensure files are in `Dictionaries/` folder
- Remove any BOM (Byte Order Mark) from files

### "Words not recognized"
- Verify exact spelling matches (case-sensitive in Devanagari)
- Check for extra spaces or invisible characters
- Ensure no blank lines within word lists

### "Corrections not working"
- Verify JSON syntax in cpair.json
- Use online JSON validator
- Check for trailing commas
- Ensure proper quote marks (")

---

## 📝 Contributing

As you work on your Ramayana manuscript:

1. **Keep notes** of frequently occurring unknown words
2. **Document** scribal conventions you discover
3. **Share** your expanded dictionaries with the community
4. **Report** systematic OCR errors for improvement

---

## 🙏 Credits

Dictionary compiled for **PANDULIPI** - Manuscript Annotation Tool
Based on:
- Valmiki Ramayana traditional texts
- Sanskrit grammar references
- Common OCR error patterns in Devanagari manuscripts

---

## 📧 Support

For questions or to contribute improvements:
- Check PANDULIPI documentation
- Review spell_check_module.py for technical details
- Use "Color Legend" in PANDULIPI for reference

---

**Happy Transcribing! 🎉**

*May your Ramayana manuscript work be blessed with accuracy and completeness!*

॥ श्रीरामजयम् ॥