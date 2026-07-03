"""
FIXED VERSION - Complete Spell Check Module for PANDULIPI

Key fixes:
1. Proper state reset on enable/disable
2. Document-level rehighlight with forced refresh
3. Clear frequency tracking between toggles
4. 4-Category UI Color Constraints
"""

import os
import json
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Set, List
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ValidationStatus(Enum):
    """Word validation status categories"""
    EMPTY = "empty"
    VALID = "valid"      # Main dictionary
    DOMAIN = "domain"    # GBook + PWords
    CPAIR = "cpair"      # Correction pairs
    INCORRECT = "incorrect" # Unknown / ASCII / Frequent / Decomposed
    MANUAL = "manual"
    PARTIAL = "partial"


@dataclass
class SubwordMatch:
    """Represents a matched substring within a word"""
    start: int
    length: int
    matched_word: str
    source: str


@dataclass
class WordCheckResult:
    """Result of word validation"""
    word: str
    status: ValidationStatus
    suggestion: Optional[str] = None
    source: Optional[str] = None
    start: int = 0
    length: int = 0
    subword_matches: List[SubwordMatch] = None
    
    def __post_init__(self):
        if self.subword_matches is None:
            self.subword_matches = []


# ============================================================================
# DICTIONARY MANAGER
# ============================================================================

class DictionaryManager:
    """Manages multiple dictionaries for spell checking"""
    
    def __init__(self, dict_dir: str = "Dictionaries"):
        self.dict_dir = Path(dict_dir)
        self.dict_dir.mkdir(exist_ok=True)
        
        self.main_dict: Set[str] = set()
        self.gbook_dict: Set[str] = set()
        self.pwords_dict: Set[str] = set()
        self.cpair_dict: Dict[str, str] = {}
        
        self._init_devanagari_classes()
        self.load_dictionaries()
    
    def _init_devanagari_classes(self):
        """Initialize Devanagari character classifications"""
        self.consonants = set('कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहळक़ख़ग़ज़ड़ढ़फ़')
        self.vowels = set('अआइईउऊऋॠऌॡएऐओऔ')
        self.vowel_signs = set('ािीुूृॄॢॣेैोौ')
        self.virama = '्'
        self.special_marks = set('ंःँ')
    
    def _is_valid_syllable_boundary(self, word: str, position: int) -> bool:
        """Check if position is a valid syllable boundary"""
        if position <= 0 or position >= len(word):
            return True
        
        before_char = word[position - 1] if position > 0 else None
        at_char = word[position]
        
        if before_char == self.virama or at_char == self.virama:
            return False
        if before_char in self.consonants and at_char in self.vowel_signs:
            return False
        if before_char in self.consonants and at_char in self.special_marks:
            return False
        if at_char in self.vowel_signs:
            return False
        
        return True
    
    def find_subword_matches(self, word: str, min_length: int = 3) -> List[SubwordMatch]:
        """Find dictionary words that match substrings"""
        if len(word) < min_length:
            return []
        
        matches = []
        word_length = len(word)
        
        for window_size in range(word_length, min_length - 1, -1):
            for start_pos in range(word_length - window_size + 1):
                end_pos = start_pos + window_size
                
                if not self._is_valid_syllable_boundary(word, start_pos):
                    continue
                if not self._is_valid_syllable_boundary(word, end_pos):
                    continue
                
                subword = word[start_pos:end_pos]
                
                if self._is_position_covered(matches, start_pos, window_size):
                    continue
                
                dict_name, _ = self.lookup(subword)
                
                if dict_name:
                    match = SubwordMatch(
                        start=start_pos,
                        length=window_size,
                        matched_word=subword,
                        source=dict_name
                    )
                    matches.append(match)
        
        matches.sort(key=lambda m: m.start)
        return matches
    
    def _is_position_covered(self, matches: List[SubwordMatch], start: int, length: int) -> bool:
        """Check if position range is already covered"""
        end = start + length
        for match in matches:
            match_end = match.start + match.length
            if not (end <= match.start or start >= match_end):
                return True
        return False
    
    def load_dictionaries(self):
        """Load all dictionary files"""
        self.main_dict = self._load_word_list("main_dict.txt")
        self.gbook_dict = self._load_word_list("gbook.txt")
        self.pwords_dict = self._load_word_list("pwords.txt")
        self.cpair_dict = self._load_correction_pairs("cpair.json")
        
        print(f"✓ Loaded dictionaries:")
        print(f"  Main: {len(self.main_dict)} words")
        print(f"  GBook: {len(self.gbook_dict)} words")
        print(f"  PWords: {len(self.pwords_dict)} words")
        print(f"  Correction pairs: {len(self.cpair_dict)}")
    
    def _load_word_list(self, filename: str) -> Set[str]:
        """Load word list from file"""
        filepath = self.dict_dir / filename
        words = set()
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word and not word.startswith('#'):
                            words.add(word)
            except Exception as e:
                print(f"⚠ Error loading {filename}: {e}")
        else:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {filename} - One word per line (Devanagari)\n")
                print(f"✓ Created empty dictionary: {filename}")
            except Exception as e:
                print(f"⚠ Could not create {filename}: {e}")
        
        return words
    
    def _load_correction_pairs(self, filename: str) -> Dict[str, str]:
        """Load correction pairs from JSON"""
        filepath = self.dict_dir / filename
        pairs = {}
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pairs = {
                        k: v for k, v in data.items()
                        if not k.startswith(('Comment', 'Format', '_'))
                    }
            except Exception as e:
                print(f"⚠ Error loading {filename}: {e}")
        else:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "_comment": "Correction pairs: incorrect → correct (Devanagari)",
                        "_format": "devanagari"
                    }, f, indent=2, ensure_ascii=False)
                print(f"✓ Created empty correction pairs: {filename}")
            except Exception as e:
                print(f"⚠ Could not create {filename}: {e}")
        
        return pairs
    
    def lookup(self, word: str) -> Tuple[Optional[str], Optional[str]]:
        """Look up word in dictionaries - ORDER MATTERS"""
        # Check GBook FIRST (before main dict)
        if word in self.gbook_dict:
            return ('gbook', word)
        if word in self.pwords_dict:
            return ('pwords', word)
        if word in self.cpair_dict:
            return ('cpair', self.cpair_dict[word])
        if word in self.main_dict:
            return ('main', word)
        return (None, None)
    
    def add_to_pwords(self, word: str) -> bool:
        """Add word to project dictionary"""
        if not word or word in self.pwords_dict:
            return False
        
        self.pwords_dict.add(word)
        
        filepath = self.dict_dir / "pwords.txt"
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(word + '\n')
            print(f"✓ Added '{word}' to PWords")
            return True
        except Exception as e:
            print(f"⚠ Error adding to PWords: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get dictionary statistics"""
        return {
            'main': len(self.main_dict),
            'gbook': len(self.gbook_dict),
            'pwords': len(self.pwords_dict),
            'cpair': len(self.cpair_dict),
            'format': 'devanagari',
            'total': len(self.main_dict) + len(self.gbook_dict) + 
                    len(self.pwords_dict) + len(self.cpair_dict)
        }


# ============================================================================
# SPELL CHECKER
# ============================================================================

class SpellChecker:
    """Main spell checking engine"""
    
    def __init__(self, dict_manager: DictionaryManager):
        self.dict_manager = dict_manager
        self.word_frequency: Dict[str, int] = defaultdict(int)
        self.frequency_threshold = 4
        self.manually_corrected: Set[str] = set()
        self.min_subword_length = 3
        self.enable_subword_matching = True
        self._session_id = 0  # Track reset sessions
    
    def reset_frequency(self):
        """Reset word frequency tracking - CRITICAL FIX"""
        print(f"SpellChecker: Resetting frequency tracking (session {self._session_id})")
        self.word_frequency.clear()
        self._session_id += 1
    
    def check_word(self, word: str) -> WordCheckResult:
        """Check a single word"""
        if not word:
            return WordCheckResult(word, ValidationStatus.EMPTY)
        
        # Manual correction check
        if word in self.manually_corrected:
            return WordCheckResult(word, ValidationStatus.MANUAL, word, 'manual')
        
        # Dictionary lookup BEFORE frequency check
        dict_name, corrected = self.dict_manager.lookup(word)
        
        if dict_name == 'gbook' or dict_name == 'pwords':
            return WordCheckResult(word, ValidationStatus.DOMAIN, word, 'domain')
        elif dict_name == 'cpair':
            return WordCheckResult(word, ValidationStatus.CPAIR, corrected, 'cpair')
        elif dict_name == 'main':
            return WordCheckResult(word, ValidationStatus.VALID, word, 'main')
        
        # Frequency is populated synchronously via update_frequencies_from_text
        # on entire blocks rather than checked word-by-word.
        
        # ASCII check / Frequent / Decomposed all fall under INCORRECT if not in dictionary
        
        # Subword matching
        if self.enable_subword_matching and len(word) >= self.min_subword_length:
            subword_matches = self.dict_manager.find_subword_matches(word, self.min_subword_length)
            
            if subword_matches:
                return WordCheckResult(
                    word, 
                    ValidationStatus.PARTIAL, 
                    word, 
                    'partial',
                    subword_matches=subword_matches
                )
        
        # Unknown falls back to INCORRECT
        return WordCheckResult(word, ValidationStatus.INCORRECT)
    
    def _try_decompose(self, word: str) -> bool:
        """Try to decompose compound word recursively"""
        for i in range(2, len(word) - 1):
            left, right = word[:i], word[i:]
            left_dict, _ = self.dict_manager.lookup(left)
            right_dict, _ = self.dict_manager.lookup(right)
            
            if left_dict and right_dict:
                return True
            if left_dict and len(right) > 3 and self._try_decompose(right):
                return True
        
        return False
    
    def check_text(self, text: str) -> List[WordCheckResult]:
        """Check entire text and return results"""
        pattern = r'[\u0900-\u097F]+|[a-zA-Z]+'
        results = []
        
        for match in re.finditer(pattern, text):
            word = match.group()
            result = self.check_word(word)
            result.start = match.start()
            result.length = len(word)
            results.append(result)
        
        return results
    
    def update_frequencies_from_text(self, text: str):
        """Update word frequencies correctly from the full text"""
        self.word_frequency.clear()
        pattern = r'[\u0900-\u097F]+|[a-zA-Z]+'
        for match in re.finditer(pattern, text):
            word = match.group()
            # We only care about frequent unknown words
            dict_name, _ = self.dict_manager.lookup(word)
            if not dict_name and word not in self.manually_corrected:
                self.word_frequency[word] += 1

    def mark_as_corrected(self, word: str):
        """Mark word as manually corrected"""
        self.manually_corrected.add(word)


# ============================================================================
# SYNTAX HIGHLIGHTER - FIXED VERSION
# ============================================================================

class SpellCheckHighlighter(QSyntaxHighlighter):
    """
    FIXED VERSION with proper state management
    
    Key fixes:
    1. Reset spell checker frequency on enable
    2. Force document refresh on state change
    3. Proper format clearing
    """
    
    def __init__(self, document, spell_checker: SpellChecker):
        super().__init__(document)
        self.spell_checker = spell_checker
        self.enabled = False
        self.manual_colors = {}
        self.formats = self._create_formats()
        self._last_enabled_state = False
        
        print("✓ SpellCheckHighlighter initialized (FIXED)")
    
    def _create_formats(self):
        """Create text formats"""
        formats = {}
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(0, 0, 0))
        formats[ValidationStatus.MANUAL] = fmt
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(0, 128, 0)) # Green
        formats[ValidationStatus.VALID] = fmt
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(0, 0, 139)) # Dark Blue
        formats[ValidationStatus.DOMAIN] = fmt
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(128, 0, 128)) # Purple
        formats[ValidationStatus.CPAIR] = fmt
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(0, 100, 100)) # Default teal for PARTIAL complex match mapping
        formats[ValidationStatus.PARTIAL] = fmt
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(255, 0, 0)) # Red
        formats[ValidationStatus.INCORRECT] = fmt
        
        return formats
    
    def enable(self, enabled: bool):
        """
        CRITICAL FIX: Reset spell checker state on enable
        """
        print(f"SpellCheckHighlighter.enable({enabled})")
        
        # State change detection
        state_changed = (enabled != self._last_enabled_state)
        
        if state_changed:
            print(f"  State changed: {self._last_enabled_state} → {enabled}")
            
            # CRITICAL: Reset frequency tracking when enabling
            if enabled:
                print("  Resetting spell checker frequency tracking")
                self.spell_checker.reset_frequency()
        
        self.enabled = enabled
        self._last_enabled_state = enabled
        
        # Force complete rehighlight
        self._force_refresh()
    
    def _force_refresh(self):
        """Force a complete document refresh"""
        try:
            doc = self.document()
            if doc:
                if self.enabled:
                    self.spell_checker.update_frequencies_from_text(doc.toPlainText())

                # Method 1: Rehighlight entire document
                super().rehighlight()
                
                # Method 2: Force layout update (ensures visual refresh)
                cursor = QTextCursor(doc)
                cursor.movePosition(QTextCursor.Start)
                doc.markContentsDirty(0, doc.characterCount())
                
                print("  Document refresh forced with updated frequencies")
        except Exception as e:
            print(f"  Error forcing refresh: {e}")
    
    def rehighlight(self):
        """Override rehighlight to ensure clean state"""
        super().rehighlight()
    
    def highlightBlock(self, text: str):
        """
        FIXED: Proper format clearing and application
        """
        if not text:
            return
        
        # ALWAYS clear format first (even when disabled)
        default_fmt = QTextCharFormat()
        default_fmt.setForeground(QColor(0, 0, 0))
        self.setFormat(0, len(text), default_fmt)
        
        # If disabled, we're done
        if not self.enabled:
            return
        
        # Get spell check results
        try:
            results = self.spell_checker.check_text(text)
        except Exception as e:
            print(f"Spell check error: {e}")
            return
        
        if not results:
            return
        
        # Apply highlighting
        for result in results:
            try:
                position = result.start
                length = result.length
                
                # Manual color override
                if position in self.manual_colors:
                    manual_length, manual_color = self.manual_colors[position]
                    if manual_length == length:
                        fmt = QTextCharFormat()
                        fmt.setForeground(manual_color)
                        self.setFormat(position, length, fmt)
                        continue
                
                # Partial matches (subword highlighting)
                if result.status == ValidationStatus.PARTIAL and result.subword_matches:
                    self._apply_partial(position, length, result.subword_matches)
                # Normal highlighting
                elif result.status in self.formats:
                    self.setFormat(position, length, self.formats[result.status])
                    
            except Exception as e:
                print(f"Error highlighting at {position}: {e}")
    
    def _apply_partial(self, position, length, subword_matches):
        """Apply partial highlighting for subword matches"""
        try:
            sources = set(m.source for m in subword_matches)
            covered = set()
            for m in subword_matches:
                for i in range(m.start, m.start + m.length):
                    covered.add(i)
            
            fully_covered = len(covered) == length
            single_source = len(sources) == 1
            
            # If fully covered by single source, use that source's color
            if fully_covered and single_source:
                source = sources.pop()
                if source == 'main':
                    fmt = self.formats[ValidationStatus.VALID]
                elif source == 'gbook' or source == 'pwords':
                    fmt = self.formats[ValidationStatus.DOMAIN]
                else: # Default unmapped partial fallback 
                    fmt = self.formats[ValidationStatus.INCORRECT]
                self.setFormat(position, length, fmt)
            else:
                # Complex partial match - apply base component color first
                base_fmt = QTextCharFormat()
                base_fmt.setForeground(QColor(0, 100, 100))
                self.setFormat(position, length, base_fmt)
                
                # Apply colors for matched subwords
                for match in subword_matches:
                    if match.source == 'main':
                        fmt = self.formats[ValidationStatus.VALID]
                    elif match.source == 'gbook' or match.source == 'pwords':
                        fmt = self.formats[ValidationStatus.DOMAIN]
                    else:
                        fmt = self.formats[ValidationStatus.INCORRECT]
                    self.setFormat(position + match.start, match.length, fmt)
                
                # Highlight unmatched parts in red
                red_fmt = self.formats[ValidationStatus.INCORRECT]
                i = 0
                while i < length:
                    if i not in covered:
                        j = i
                        while j < length and j not in covered:
                            j += 1
                        self.setFormat(position + i, j - i, red_fmt)
                        i = j
                    else:
                        i += 1
                        
        except Exception as e:
            print(f"Error in partial highlighting: {e}")
    
    def set_manual_color(self, position: int, length: int, color: QColor):
        """Set manual color override"""
        self.manual_colors[position] = (length, color)
        self.rehighlight()
    
    def get_color_legend(self):
        """Get color legend text"""
        return """
<h3>Color Legend</h3>
<table cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
<tr>
    <td width="20"><div style="background-color: rgb(0, 128, 0); width: 15px; height: 15px; border: 1px solid black;"></div></td>
    <td><b>Main Dictionary Words</b></td>
    <td><span style="color: rgb(0, 128, 0);">(Green)</span></td>
</tr>
<tr>
    <td><div style="background-color: rgb(0, 0, 139); width: 15px; height: 15px; border: 1px solid black;"></div></td>
    <td><b>Domain Dictionary Words</b></td>
    <td><span style="color: rgb(0, 0, 139);">(Dark Blue)</span></td>
</tr>
<tr>
    <td><div style="background-color: rgb(128, 0, 128); width: 15px; height: 15px; border: 1px solid black;"></div></td>
    <td><b>Correction Pairs</b></td>
    <td><span style="color: rgb(128, 0, 128);">(Purple)</span></td>
</tr>
<tr>
    <td><div style="background-color: rgb(255, 0, 0); width: 15px; height: 15px; border: 1px solid black;"></div></td>
    <td><b>Incorrect Words</b></td>
    <td><span style="color: rgb(255, 0, 0);">(Red)</span></td>
</tr>
</table>
<br>
<b>Partial matches show:</b><br>
- Matched subwords in their respective dictionary colors<br>
- Unmatched parts in Red (Incorrect)
"""


if __name__ == "__main__":
    print("Spell Check Module Loaded (FIXED version)")
