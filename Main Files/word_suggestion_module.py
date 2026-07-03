#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Suggestion Module
======================

Provides real-time word suggestions using Trie data structure with fuzzy matching
based on Levenshtein distance algorithm.

Features:
- Fast prefix-based word lookup
- Fuzzy matching for typos and variations
- Integration with GBook dictionary
- Real-time suggestions while typing
- Keyboard shortcut (Ctrl+C) for selected word suggestions
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional


# ═══════════════════════════════════════════════════════════════════
# TRIE NODE
# ═══════════════════════════════════════════════════════════════════
class TrieNode:
    """Node in the Trie data structure"""
    
    def __init__(self):
        self.word = None
        self.children = {}
        self.frequency = 0  # For ranking suggestions
    
    def insert(self, word: str, frequency: int = 1):
        """Insert a word into the Trie"""
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        
        node.word = word
        node.frequency = frequency


# ═══════════════════════════════════════════════════════════════════
# WORD SUGGESTION ENGINE
# ═══════════════════════════════════════════════════════════════════
class WordSuggestionEngine:
    """
    Trie-based word suggestion engine with fuzzy matching
    
    Uses Levenshtein distance algorithm for finding similar words
    when exact prefix matches aren't available.
    """
    
    def __init__(self, dictionary_path: str):
        """
        Initialize suggestion engine
        
        Args:
            dictionary_path: Path to dictionary file (e.g., gbook.txt)
        """
        self.trie = TrieNode()
        self.word_count = 0
        self.dictionary_path = dictionary_path
        self.max_suggestions = 10
        self.enabled = False
        
        # Load dictionary
        self.load_dictionary()
    
    def load_dictionary(self):
        """Load dictionary into Trie structure"""
        if not os.path.exists(self.dictionary_path):
            print(f"⚠ Dictionary not found: {self.dictionary_path}")
            return
        
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.trie.insert(word)
                        self.word_count += 1
            
            self.enabled = True
            print(f"✓ Loaded {self.word_count} words into suggestion engine")
            
        except Exception as e:
            print(f"✗ Error loading dictionary: {e}")
            self.enabled = False
    
    def get_prefix_suggestions(self, prefix: str, max_results: int = 10) -> List[Tuple[str, int]]:
        """
        Get word suggestions based on prefix
        
        Args:
            prefix: Input prefix
            max_results: Maximum number of suggestions
            
        Returns:
            List of (word, frequency) tuples
        """
        if not prefix or not self.enabled:
            return []
        
        # Navigate to prefix node
        node = self.trie
        for letter in prefix:
            if letter not in node.children:
                # Prefix not found - return fuzzy matches instead
                return self.get_fuzzy_suggestions(prefix, max_results)
            node = node.children[letter]
        
        # Collect all words with this prefix
        results = []
        self._collect_words(node, results, max_results)
        
        # Sort by frequency (descending) and then alphabetically
        results.sort(key=lambda x: (-x[1], x[0]))
        
        return results[:max_results]
    
    def _collect_words(self, node: TrieNode, results: List[Tuple[str, int]], max_results: int):
        """
        Recursively collect all words from a node
        
        Args:
            node: Current Trie node
            results: List to append results to
            max_results: Maximum results to collect
        """
        if len(results) >= max_results:
            return
        
        if node.word is not None:
            results.append((node.word, node.frequency))
        
        for letter in sorted(node.children.keys()):
            if len(results) >= max_results:
                break
            self._collect_words(node.children[letter], results, max_results)
    
    def get_fuzzy_suggestions(self, word: str, max_cost: int = 2, max_results: int = 10) -> List[Tuple[str, int]]:
        """
        Get fuzzy word suggestions using Levenshtein distance
        
        Args:
            word: Input word
            max_cost: Maximum edit distance (default: 2)
            max_results: Maximum number of suggestions
            
        Returns:
            List of (word, distance) tuples sorted by distance
        """
        if not word or not self.enabled:
            return []
        
        # Build first row (distance from empty string)
        current_row = list(range(len(word) + 1))
        results = []
        
        # Recursively search each branch of the trie
        for letter in self.trie.children:
            self._search_recursive(
                self.trie.children[letter],
                letter,
                word,
                current_row,
                results,
                max_cost
            )
        
        # Sort by edit distance (ascending) and then alphabetically
        results.sort(key=lambda x: (x[1], x[0]))
        
        return results[:max_results]
    
    def _search_recursive(self, node: TrieNode, letter: str, word: str, 
                         previous_row: List[int], results: List[Tuple[str, int]], 
                         max_cost: int):
        """
        Recursive helper for fuzzy search using dynamic programming
        
        This implements the Levenshtein distance algorithm incrementally
        as we traverse the Trie.
        
        Args:
            node: Current Trie node
            letter: Current letter
            word: Target word
            previous_row: Previous row of edit distance matrix
            results: List to append results to
            max_cost: Maximum allowed edit distance
        """
        columns = len(word) + 1
        current_row = [previous_row[0] + 1]
        
        # Build one row for the letter, with a column for each letter in the target word
        for column in range(1, columns):
            insert_cost = current_row[column - 1] + 1
            delete_cost = previous_row[column] + 1
            
            if word[column - 1] != letter:
                replace_cost = previous_row[column - 1] + 1
            else:
                replace_cost = previous_row[column - 1]
            
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        
        # If the last entry in the row indicates the optimal cost is less than
        # the maximum cost, and there is a word in this trie node, then add it
        if current_row[-1] <= max_cost and node.word is not None:
            results.append((node.word, current_row[-1]))
        
        # If any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie
        if min(current_row) <= max_cost:
            for child_letter in node.children:
                self._search_recursive(
                    node.children[child_letter],
                    child_letter,
                    word,
                    current_row,
                    results,
                    max_cost
                )
    
    def get_suggestions_for_word(self, word: str, max_results: int = 10) -> List[Tuple[str, str, int]]:
        """
        Get comprehensive suggestions for a word
        
        First tries prefix matching, then falls back to fuzzy matching.
        
        Args:
            word: Input word
            max_results: Maximum number of suggestions
            
        Returns:
            List of (word, match_type, score) tuples where:
            - match_type is either 'prefix' or 'fuzzy'
            - score is frequency for prefix matches, edit distance for fuzzy
        """
        if not word or not self.enabled:
            return []
        
        # Try prefix matching first
        prefix_results = self.get_prefix_suggestions(word, max_results)
        
        if prefix_results:
            # Convert to common format
            return [(w, 'prefix', freq) for w, freq in prefix_results]
        
        # Fall back to fuzzy matching
        fuzzy_results = self.get_fuzzy_suggestions(word, max_cost=2, max_results=max_results)
        
        # Convert to common format (negate distance so higher is better)
        return [(w, 'fuzzy', -dist) for w, dist in fuzzy_results]
    
    def is_word_in_dictionary(self, word: str) -> bool:
        """
        Check if a word exists in the dictionary
        
        Args:
            word: Word to check
            
        Returns:
            True if word exists, False otherwise
        """
        if not word or not self.enabled:
            return False
        
        node = self.trie
        for letter in word:
            if letter not in node.children:
                return False
            node = node.children[letter]
        
        return node.word is not None


# ═══════════════════════════════════════════════════════════════════
# SUGGESTION MANAGER
# ═══════════════════════════════════════════════════════════════════
class SuggestionManager:
    """
    High-level manager for word suggestions
    
    Coordinates between multiple dictionary sources and provides
    unified suggestion interface.
    """
    
    def __init__(self, dictionaries_dir: str = "Dictionaries"):
        """
        Initialize suggestion manager
        
        Args:
            dictionaries_dir: Directory containing dictionary files
        """
        self.dictionaries_dir = dictionaries_dir
        self.engines = {}
        self.enabled = False
        
        # Initialize engines for different dictionaries
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize suggestion engines for available dictionaries"""
        # GBook dictionary (primary source for suggestions)
        gbook_path = os.path.join(self.dictionaries_dir, "gbook.txt")
        if os.path.exists(gbook_path):
            self.engines['gbook'] = WordSuggestionEngine(gbook_path)
            if self.engines['gbook'].enabled:
                self.enabled = True
                print(f"✓ GBook suggestion engine initialized")
        
        # Could add more dictionaries here
        # main_dict_path = os.path.join(self.dictionaries_dir, "main_dict.txt")
        # if os.path.exists(main_dict_path):
        #     self.engines['main'] = WordSuggestionEngine(main_dict_path)
    
    def get_suggestions(self, word: str, max_results: int = 10) -> List[Tuple[str, str]]:
        """
        Get suggestions from all available engines
        
        Args:
            word: Input word
            max_results: Maximum number of suggestions
            
        Returns:
            List of (word, source) tuples
        """
        if not word or not self.enabled:
            return []
        
        all_suggestions = []
        seen_words = set()
        
        # Collect suggestions from all engines
        for source, engine in self.engines.items():
            suggestions = engine.get_suggestions_for_word(word, max_results)
            
            for suggested_word, match_type, score in suggestions:
                if suggested_word not in seen_words:
                    all_suggestions.append((suggested_word, source, match_type, score))
                    seen_words.add(suggested_word)
        
        # Sort by score (descending)
        all_suggestions.sort(key=lambda x: -x[3])
        
        # Return top results
        return [(word, source) for word, source, _, _ in all_suggestions[:max_results]]
    
    def is_valid_word(self, word: str) -> bool:
        """
        Check if word is valid in any dictionary
        
        Args:
            word: Word to check
            
        Returns:
            True if valid, False otherwise
        """
        if not word or not self.enabled:
            return False
        
        for engine in self.engines.values():
            if engine.is_word_in_dictionary(word):
                return True
        
        return False
