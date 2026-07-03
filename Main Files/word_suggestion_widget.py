#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Suggestion Widget Integration
====================================

Provides UI components and integration logic for word suggestions in PANDULIPI.

Features:
- Popup suggestion widget
- Auto-complete while typing
- Ctrl+C shortcut for selected word suggestions
- Keyboard navigation (Up/Down arrows, Enter to select)
"""

from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QFrame, 
                             QShortcut, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt5.QtGui import QKeySequence, QFont, QColor, QPalette, QTextCursor
from typing import Optional, List, Tuple


# ═══════════════════════════════════════════════════════════════════
# SUGGESTION POPUP WIDGET
# ═══════════════════════════════════════════════════════════════════
class SuggestionPopup(QListWidget):
    """
    Popup widget for displaying word suggestions
    
    Features:
    - Appears near cursor position
    - Keyboard navigation
    - Mouse selection
    - Auto-hides when appropriate
    """
    
    suggestion_selected = pyqtSignal(str)  # Emitted when user selects a suggestion
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setMaximumHeight(200)
        self.setMaximumWidth(300)
        self.setMinimumWidth(150)
        
        # Styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 2px solid #4A90E2;
                border-radius: 4px;
                font-size: 14px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #E3F2FD;
            }
        """)
        
        # Set font
        font = QFont()
        font.setFamily("Noto Sans Devanagari")
        font.setPointSize(12)
        self.setFont(font)
        
        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)
    
    def show_suggestions(self, suggestions: List[Tuple[str, str]], cursor_rect: QRect):
        """
        Display suggestions near cursor
        
        Args:
            suggestions: List of (word, source) tuples
            cursor_rect: Rectangle representing cursor position
        """
        self.clear()
        
        if not suggestions:
            self.hide()
            return
        
        # Populate list
        for word, source in suggestions:
            item = QListWidgetItem(word)
            item.setData(Qt.UserRole, source)  # Store source
            
            # Color-code by source
            if source == 'gbook':
                item.setForeground(QColor("#2E7D32"))  # Dark green
            
            self.addItem(item)
        
        # Select first item
        if self.count() > 0:
            self.setCurrentRow(0)
        
        # Position popup near cursor
        self._position_popup(cursor_rect)
        
        # Show popup
        self.show()
        self.setFocus()
    
    def _position_popup(self, cursor_rect: QRect):
        """
        Position popup near cursor
        
        Args:
            cursor_rect: Rectangle representing cursor position
        """
        # Calculate popup position
        x = cursor_rect.left()
        y = cursor_rect.bottom() + 5  # 5px below cursor
        
        # Ensure popup stays on screen
        screen_geometry = QApplication.desktop().availableGeometry()
        
        if x + self.width() > screen_geometry.right():
            x = screen_geometry.right() - self.width()
        
        if y + self.height() > screen_geometry.bottom():
            y = cursor_rect.top() - self.height() - 5  # Show above cursor
        
        self.move(x, y)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click"""
        self.suggestion_selected.emit(item.text())
        self.hide()
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Select current item
            current_item = self.currentItem()
            if current_item:
                self.suggestion_selected.emit(current_item.text())
                self.hide()
        elif event.key() == Qt.Key_Escape:
            # Hide popup
            self.hide()
        else:
            # Default behavior (arrow keys, etc.)
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """Hide popup when focus is lost"""
        super().focusOutEvent(event)
        self.hide()


# ═══════════════════════════════════════════════════════════════════
# TEXT EDIT WITH SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════
def add_suggestions_to_text_edit(text_edit, suggestion_manager):
    """
    Add suggestion functionality to existing QTextEdit instance
    
    Args:
        text_edit: QTextEdit instance
        suggestion_manager: SuggestionManager instance
    
    Returns:
        Modified text_edit with suggestion functionality
    """
    # Store original keyPressEvent
    original_key_press = text_edit.keyPressEvent
    
    # Initialize suggestion attributes
    text_edit.suggestion_manager = suggestion_manager
    text_edit.suggestion_popup = SuggestionPopup(text_edit)
    text_edit.suggestion_enabled = True
    text_edit.suggestion_timer = QTimer()
    text_edit.suggestion_timer.setSingleShot(True)
    
    # Configuration
    text_edit.suggestion_delay = 500  # milliseconds
    text_edit.min_word_length = 2
    
    # Helper methods
    def get_current_word():
        """Get word at cursor position"""
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText().strip()
        return word if word else None
    
    def show_suggestions_for_current_word():
        """Show suggestions for word being typed"""
        word = get_current_word()
        
        if not word or len(word) < text_edit.min_word_length:
            text_edit.suggestion_popup.hide()
            return
        
        # Get suggestions
        suggestions = text_edit.suggestion_manager.get_suggestions(word, max_results=10)
        
        if not suggestions:
            text_edit.suggestion_popup.hide()
            return
        
        # Get cursor position in global coordinates
        cursor = text_edit.textCursor()
        cursor_rect = text_edit.cursorRect(cursor)
        global_cursor_rect = QRect(
            text_edit.mapToGlobal(cursor_rect.topLeft()),
            cursor_rect.size()
        )
        
        # Show popup
        text_edit.suggestion_popup.show_suggestions(suggestions, global_cursor_rect)
    
    def show_suggestions_manual():
        """Show suggestions manually (Ctrl+Space)"""
        text_edit.suggestion_timer.stop()
        show_suggestions_for_current_word()
    
    def show_suggestions_for_selected_word():
        """Show suggestions for selected word (Ctrl+Shift+C)"""
        cursor = text_edit.textCursor()
        
        if not cursor.hasSelection():
            show_suggestions_manual()
            return
        
        selected_text = cursor.selectedText().strip()
        if not selected_text:
            return
        
        # Get suggestions
        suggestions = text_edit.suggestion_manager.get_suggestions(selected_text, max_results=10)
        
        if not suggestions:
            return
        
        # Get cursor position
        cursor_rect = text_edit.cursorRect(cursor)
        global_cursor_rect = QRect(
            text_edit.mapToGlobal(cursor_rect.topLeft()),
            cursor_rect.size()
        )
        
        # Show popup
        text_edit.suggestion_popup.show_suggestions(suggestions, global_cursor_rect)
    
    def insert_suggestion(suggestion: str):
        """Insert selected suggestion"""
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText(suggestion)
        text_edit.setTextCursor(cursor)
    
    def enable_suggestions(enabled: bool):
        """Enable or disable auto-suggestions"""
        text_edit.suggestion_enabled = enabled
        if not enabled:
            text_edit.suggestion_popup.hide()
            text_edit.suggestion_timer.stop()
    
    # Override keyPressEvent
    def new_key_press_event(event):
        # Call original implementation first
        original_key_press(event)
        
        # Check if suggestions are enabled
        if not text_edit.suggestion_enabled or not text_edit.suggestion_manager.enabled:
            return
        
        # Hide popup on certain keys
        if event.key() in (Qt.Key_Escape, Qt.Key_Left, Qt.Key_Right, 
                          Qt.Key_Home, Qt.Key_End):
            text_edit.suggestion_popup.hide()
            return
        
        # Trigger suggestions on typing
        if event.text() and event.text().isalnum():
            # Reset timer
            text_edit.suggestion_timer.stop()
            text_edit.suggestion_timer.start(text_edit.suggestion_delay)
        elif event.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter):
            # Hide on word boundary
            text_edit.suggestion_popup.hide()
            text_edit.suggestion_timer.stop()
    
    # Attach methods to text_edit instance
    text_edit.get_current_word = get_current_word
    text_edit.show_suggestions_for_current_word = show_suggestions_for_current_word
    text_edit.show_suggestions_manual = show_suggestions_manual
    text_edit.show_suggestions_for_selected_word = show_suggestions_for_selected_word
    text_edit.insert_suggestion = insert_suggestion
    text_edit.enable_suggestions = enable_suggestions
    
    # Replace keyPressEvent
    text_edit.keyPressEvent = new_key_press_event
    
    # Connect signals
    text_edit.suggestion_timer.timeout.connect(show_suggestions_for_current_word)
    text_edit.suggestion_popup.suggestion_selected.connect(insert_suggestion)
    
    # Keyboard shortcuts
    suggestion_shortcut = QShortcut(QKeySequence("Ctrl+Space"), text_edit)
    suggestion_shortcut.activated.connect(show_suggestions_manual)
    
    selected_word_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), text_edit)
    selected_word_shortcut.activated.connect(show_suggestions_for_selected_word)
    
    # Store shortcuts to prevent garbage collection
    text_edit._suggestion_shortcut = suggestion_shortcut
    text_edit._selected_word_shortcut = selected_word_shortcut
    
    return text_edit