"""
Text postprocessing utilities for OCR output.

This module provides text cleanup and formatting utilities to improve
extracted text quality, including:
- Whitespace normalization
- Line break fixing
- Spell checking (Phase 2 - optional)
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Optional: Spell checker (Phase 2)
try:
    from spellchecker import SpellChecker
    SPELLCHECKER_AVAILABLE = True
except ImportError:
    SPELLCHECKER_AVAILABLE = False
    logger.info("pyspellchecker not installed. Spell checking disabled.")


def remove_extra_whitespace(text: str) -> str:
    """
    Remove excessive whitespace from text.

    Collapses:
    - Multiple consecutive spaces to single space
    - Multiple tabs to single space
    - Multiple blank lines to single newline

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace
    """
    # Remove multiple spaces (but preserve line structure)
    text = re.sub(r' +', ' ', text)

    # Replace tabs with space
    text = text.replace('\t', ' ')

    # Remove trailing/leading whitespace on each line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)

    return text


def fix_line_breaks(text: str) -> str:
    """
    Normalize line breaks to Unix style (LF only).

    Converts:
    - Windows line breaks (\\r\\n) to LF (\\n)
    - Old Mac style (\\r) to LF (\\n)

    Args:
        text: Input text

    Returns:
        Text with normalized line breaks
    """
    # Windows CRLF to LF
    text = text.replace('\r\n', '\n')

    # Old Mac CR to LF
    text = text.replace('\r', '\n')

    return text


def remove_empty_lines(text: str) -> str:
    """
    Remove lines containing only whitespace.

    Args:
        text: Input text

    Returns:
        Text without empty lines
    """
    lines = text.split('\n')
    # Keep only non-empty lines
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)


def fix_common_ocr_errors(text: str) -> str:
    """
    Fix common OCR mistakes.

    Common substitutions:
    - '|' (pipe) often confused with 'l' (lowercase L) or 'I' (uppercase i)
    - '0' (zero) confused with 'O' (uppercase O)
    - Misplaced spaces in common words

    Args:
        text: Input text

    Returns:
        Text with common OCR errors corrected

    Note:
        This is a basic set. Phase 2 adds spell checking.
    """
    # Common patterns from OCR errors
    # Be conservative to avoid changing correct text
    
    # Fix common confusion between O and 0 in specific contexts
    # (only at word boundaries)
    patterns = [
        (r'\b0ne\b', 'One'),          # 0ne -> One
        (r'\b0f\b', 'Of'),            # 0f -> Of
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def apply_spell_correction(text: str, language: str = "en") -> str:
    """
    Apply spell correction to extracted text.

    Phase 2: Optional spell checking via pyspellchecker

    Args:
        text: Input text
        language: Language code (default: "en" for English)

    Returns:
        Text with spell corrections applied (if available)

    Note:
        Returns original text if spellchecker is not available.
        Uses word-level correction to preserve formatting.
    """
    if not SPELLCHECKER_AVAILABLE:
        logger.debug("Spell checker not available. Returning original text.")
        return text

    try:
        spell = SpellChecker(language=language)

        # Split into words while preserving formatting
        words = text.split()
        corrected_words = []

        for word in words:
            # Extract actual word from punctuation
            stripped = word.strip('.,!?;:"""\'')

            if stripped and stripped.lower() not in spell:
                # Find closest match
                correction = spell.correction(stripped.lower())
                if correction:
                    # Preserve original case for first letter
                    if stripped[0].isupper():
                        correction = correction.capitalize()
                    
                    # Replace in original word (preserving punctuation)
                    corrected_word = word.replace(stripped, correction)
                    corrected_words.append(corrected_word)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)

        return " ".join(corrected_words)

    except Exception as e:
        logger.warning(f"Spell correction failed: {e}. Returning original text.")
        return text


def normalize_quotes(text: str) -> str:
    """
    Normalize quotes to standard ASCII style.

    Converts smart/curly quotes to straight quotes:
    - '" ` to '
    - " and " to "

    Args:
        text: Input text

    Returns:
        Text with normalized quotes
    """
    # Convert fancy quotes to ASCII
    text = text.replace('"', '"')  # Left double quote
    text = text.replace('"', '"')  # Right double quote
    text = text.replace(''', "'")  # Left single quote
    text = text.replace(''', "'")  # Right single quote
    text = text.replace('`', "'")  # Backtick
    text = text.replace('´', "'")  # Acute accent

    return text


def clean_text(
    text: str,
    remove_extra_spaces: bool = True,
    fix_breaks: bool = True,
    remove_blanks: bool = False,
    normalize_quotes_mode: bool = True,
) -> str:
    """
    Apply full text postprocessing pipeline.

    Args:
        text: Input OCR text
        remove_extra_spaces: Collapse multiple spaces/tabs
        fix_breaks: Normalize line endings
        remove_blanks: Remove empty lines
        normalize_quotes_mode: Convert smart quotes to ASCII

    Returns:
        Cleaned text ready for display/export
    """
    if not isinstance(text, str):
        text = str(text)

    # Apply preprocessing steps
    if normalize_quotes_mode:
        text = normalize_quotes(text)

    if fix_breaks:
        text = fix_line_breaks(text)

    if remove_extra_spaces:
        text = remove_extra_whitespace(text)

    if remove_blanks:
        text = remove_empty_lines(text)

    return text


def get_text_stats(text: str) -> dict:
    """
    Generate statistics about extracted text.

    Args:
        text: Input text

    Returns:
        Dictionary with various text metrics
    """
    lines = text.split('\n')
    words = text.split()
    sentences = text.split('.')

    return {
        "character_count": len(text),
        "word_count": len(words),
        "line_count": len([l for l in lines if l.strip()]),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "average_line_length": sum(len(l) for l in lines) / max(len(lines), 1),
    }


def truncate_text(text: str, max_chars: Optional[int] = None, max_lines: Optional[int] = None) -> str:
    """
    Truncate text to specified limits.

    Useful for preview display in UI.

    Args:
        text: Input text
        max_chars: Maximum characters (None = no limit)
        max_lines: Maximum lines (None = no limit)

    Returns:
        Truncated text
    """
    # Limit by lines
    if max_lines:
        lines = text.split('\n')
        text = '\n'.join(lines[:max_lines])

    # Limit by characters
    if max_chars:
        text = text[:max_chars]
        if len(text) == max_chars:
            text += "..."

    return text
