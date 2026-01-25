"""
Enhanced error handling for DesiLang with bilingual messages.

This module provides custom exception classes with detailed error messages
in both English and Hindi/Urdu, along with helpful suggestions for common mistakes.

Author: DesiLang Team
Version: 2.0
"""

from typing import Optional, List
from enum import Enum


class ErrorLanguage(Enum):
    """Language for error messages."""
    ENGLISH = "en"
    HINDI = "hi"
    BILINGUAL = "both"


# Global setting for error message language
ERROR_LANGUAGE = ErrorLanguage.BILINGUAL


class DesiLangError(Exception):
    """Base exception for all DesiLang errors.
    
    Provides formatted error messages with line/column information and
    optional suggestions in English and/or Hindi.
    
    Attributes:
        message_en: Error message in English
        message_hi: Error message in Hindi/Urdu (optional)
        line: Line number where error occurred
        column: Column number where error occurred
        suggestion_en: Helpful suggestion in English (optional)
        suggestion_hi: Helpful suggestion in Hindi (optional)
    """
    
    def __init__(
        self,
        message_en: str,
        message_hi: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        suggestion_en: Optional[str] = None,
        suggestion_hi: Optional[str] = None
    ):
        """Initialize error with bilingual messages.
        
        Args:
            message_en: Error message in English (required)
            message_hi: Error message in Hindi/Urdu (optional)
            line: Line number in source code
            column: Column number in source code
            suggestion_en: Helpful suggestion in English
            suggestion_hi: Helpful suggestion in Hindi
        """
        self.message_en = message_en
        self.message_hi = message_hi or message_en  # Fallback to English
        self.line = line
        self.column = column
        self.suggestion_en = suggestion_en
        self.suggestion_hi = suggestion_hi
        
        super().__init__(self.format_message())
    
    def format_message(self, language: Optional[ErrorLanguage] = None) -> str:
        """Format error message with location and suggestions.
        
        Args:
            language: Override global language setting (optional)
            
        Returns:
            Formatted error message string
        """
        lang = language or ERROR_LANGUAGE
        parts = []
        
        # Location information
        if self.line is not None:
            location = f"Line {self.line}"
            if self.column is not None:
                location += f", Column {self.column}"
            parts.append(location)
        
        # Error message
        if lang == ErrorLanguage.ENGLISH:
            parts.append(self.message_en)
        elif lang == ErrorLanguage.HINDI:
            parts.append(self.message_hi)
        else:  # BILINGUAL
            parts.append(f"{self.message_en}\n{self.message_hi}")
        
        # Suggestions
        if self.suggestion_en or self.suggestion_hi:
            if lang == ErrorLanguage.ENGLISH and self.suggestion_en:
                parts.append(f"Suggestion: {self.suggestion_en}")
            elif lang == ErrorLanguage.HINDI and self.suggestion_hi:
                parts.append(f"सुझाव: {self.suggestion_hi}")
            elif lang == ErrorLanguage.BILINGUAL:
                if self.suggestion_en:
                    parts.append(f"Suggestion: {self.suggestion_en}")
                if self.suggestion_hi:
                    parts.append(f"सुझाव: {self.suggestion_hi}")
        
        return ": ".join(parts) if len(parts) > 1 else parts[0] if parts else "Unknown error"


class LexerError(DesiLangError):
    """Error during tokenization/lexical analysis.
    
    Examples:
        - Unterminated string
        - Invalid character
        - Malformed number
    """
    
    @staticmethod
    def unterminated_string(line: int, column: int, quote: str) -> 'LexerError':
        """Create error for unterminated string."""
        return LexerError(
            message_en=f"Unterminated string (missing closing {quote})",
            message_hi=f"अधूरा स्ट्रिंग (बंद करने वाला {quote} गायब है)",
            line=line,
            column=column,
            suggestion_en=f"Add a closing {quote} at the end of the string",
            suggestion_hi=f"स्ट्रिंग के अंत में {quote} जोड़ें"
        )
    
    @staticmethod
    def unexpected_character(char: str, line: int, column: int) -> 'LexerError':
        """Create error for unexpected character."""
        return LexerError(
            message_en=f"Unexpected character: '{char}'",
            message_hi=f"अनपेक्षित अक्षर: '{char}'",
            line=line,
            column=column,
            suggestion_en="Check for typos or unsupported characters",
            suggestion_hi="टाइपो या असमर्थित अक्षरों की जांच करें"
        )
    
    @staticmethod
    def invalid_number(text: str, line: int, column: int) -> 'LexerError':
        """Create error for malformed number."""
        return LexerError(
            message_en=f"Invalid number format: '{text}'",
            message_hi=f"गलत संख्या प्रारूप: '{text}'",
            line=line,
            column=column,
            suggestion_en="Numbers should be like: 42, 3.14, -10",
            suggestion_hi="संख्याएं इस तरह होनी चाहिए: 42, 3.14, -10"
        )


class ParserError(DesiLangError):
    """Error during parsing/syntax analysis.
    
    Examples:
        - Missing semicolon
        - Unexpected token
        - Incomplete expression
    """
    
    @staticmethod
    def unexpected_token(expected: str, got: str, line: int, column: int) -> 'ParserError':
        """Create error for unexpected token."""
        return ParserError(
            message_en=f"Expected '{expected}', got '{got}'",
            message_hi=f"अपेक्षित था '{expected}', मिला '{got}'",
            line=line,
            column=column
        )
    
    @staticmethod
    def missing_token(token: str, line: int, column: int) -> 'ParserError':
        """Create error for missing required token."""
        return ParserError(
            message_en=f"Missing '{token}'",
            message_hi=f"'{token}' गायब है",
            line=line,
            column=column
        )
    
    @staticmethod
    def invalid_syntax(context: str, line: int, column: int) -> 'ParserError':
        """Create error for invalid syntax."""
        return ParserError(
            message_en=f"Invalid syntax in {context}",
            message_hi=f"{context} में गलत सिंटैक्स",
            line=line,
            column=column
        )


class RuntimeError(DesiLangError):
    """Error during interpretation/execution.
    
    Examples:
        - Division by zero
        - Type mismatch
        - Undefined variable
    """
    pass


class TypeError(RuntimeError):
    """Type mismatch error.
    
    Examples:
        - Adding string to number
        - Calling non-function
        - Invalid operand types
    """
    
    @staticmethod
    def invalid_operation(op: str, type1: str, type2: str, line: Optional[int] = None) -> 'TypeError':
        """Create error for invalid operation between types."""
        return TypeError(
            message_en=f"Cannot perform '{op}' between {type1} and {type2}",
            message_hi=f"{type1} और {type2} के बीच '{op}' नहीं कर सकते",
            line=line,
            suggestion_en=f"Convert values to compatible types first",
            suggestion_hi="पहले मानों को संगत प्रकारों में बदलें"
        )
    
    @staticmethod
    def not_callable(type_name: str, line: Optional[int] = None) -> 'TypeError':
        """Create error for calling non-function."""
        return TypeError(
            message_en=f"'{type_name}' is not callable (not a function)",
            message_hi=f"'{type_name}' कॉल करने योग्य नहीं है (फंक्शन नहीं है)",
            line=line,
            suggestion_en="Only functions can be called with ()",
            suggestion_hi="केवल फंक्शन को () से कॉल किया जा सकता है"
        )
    
    @staticmethod
    def not_iterable(type_name: str, line: Optional[int] = None) -> 'TypeError':
        """Create error for iterating non-iterable."""
        return TypeError(
            message_en=f"'{type_name}' is not iterable",
            message_hi=f"'{type_name}' पर लूप नहीं चला सकते",
            line=line,
            suggestion_en="Only lists can be used in for loops",
            suggestion_hi="केवल लिस्ट पर for लूप चला सकते हैं"
        )


class NameError(RuntimeError):
    """Undefined variable/function error."""
    
    def __init__(
        self,
        name: str,
        line: Optional[int] = None,
        similar_names: Optional[List[str]] = None
    ):
        """Initialize name error with suggestions.
        
        Args:
            name: Undefined variable/function name
            line: Line number
            similar_names: List of similar names for "did you mean?" suggestions
        """
        suggestion_en = None
        suggestion_hi = None
        
        if similar_names:
            suggestion_en = f"Did you mean: {', '.join(similar_names[:3])}?"
            suggestion_hi = f"क्या आपका मतलब था: {', '.join(similar_names[:3])}?"
        
        super().__init__(
            message_en=f"Undefined variable or function: '{name}'",
            message_hi=f"अपरिभाषित वेरिएबल या फंक्शन: '{name}'",
            line=line,
            suggestion_en=suggestion_en,
            suggestion_hi=suggestion_hi
        )


class DivisionByZeroError(RuntimeError):
    """Division by zero error."""
    
    def __init__(self, line: Optional[int] = None):
        super().__init__(
            message_en="Division by zero",
            message_hi="शून्य से भाग",
            line=line,
            suggestion_en="Check if the denominator is zero before dividing",
            suggestion_hi="भाग देने से पहले जांचें कि हर शून्य तो नहीं है"
        )


class IndexError(RuntimeError):
    """List index out of bounds error."""
    
    def __init__(self, index: int, length: int, line: Optional[int] = None):
        super().__init__(
            message_en=f"Index {index} is out of bounds for list of length {length}",
            message_hi=f"इंडेक्स {index} लंबाई {length} की लिस्ट के लिए सीमा से बाहर है",
            line=line,
            suggestion_en=f"Valid indices are 0 to {length - 1}",
            suggestion_hi=f"वैध इंडेक्स 0 से {length - 1} तक हैं"
        )


class AttributeError(RuntimeError):
    """Attribute/property not found error."""
    
    def __init__(self, obj_type: str, attr: str, line: Optional[int] = None):
        super().__init__(
            message_en=f"'{obj_type}' object has no attribute '{attr}'",
            message_hi=f"'{obj_type}' ऑब्जेक्ट में '{attr}' एट्रिब्यूट नहीं है",
            line=line
        )


class FileIOError(RuntimeError):
    """File I/O operation error."""
    
    def __init__(self, operation: str, filename: str, reason: str, line: Optional[int] = None):
        super().__init__(
            message_en=f"Failed to {operation} file '{filename}': {reason}",
            message_hi=f"फाइल '{filename}' को {operation} करने में विफल: {reason}",
            line=line
        )


class ImportError(RuntimeError):
    """Module import error."""
    
    def __init__(self, module: str, reason: str, line: Optional[int] = None):
        super().__init__(
            message_en=f"Cannot import module '{module}': {reason}",
            message_hi=f"मॉड्यूल '{module}' इम्पोर्ट नहीं कर सकते: {reason}",
            line=line,
            suggestion_en="Check if the file exists and has .dl extension",
            suggestion_hi="जांचें कि फाइल मौजूद है और .dl एक्सटेंशन है"
        )


class RecursionError(RuntimeError):
    """Maximum recursion depth exceeded."""
    
    def __init__(self, max_depth: int, line: Optional[int] = None):
        super().__init__(
            message_en=f"Maximum recursion depth ({max_depth}) exceeded",
            message_hi=f"अधिकतम रिकर्शन गहराई ({max_depth}) पार हो गई",
            line=line,
            suggestion_en="Check for infinite recursion in your code",
            suggestion_hi="अपने कोड में अनंत रिकर्शन की जांच करें"
        )


class UserException(RuntimeError):
    """User-thrown exception via 'fenko' keyword."""
    
    def __init__(self, message: any, line: Optional[int] = None):
        """Initialize user exception.
        
        Args:
            message: User-provided error message (any type)
            line: Line where exception was thrown
        """
        msg_str = str(message)
        super().__init__(
            message_en=f"Exception: {msg_str}",
            message_hi=f"अपवाद: {msg_str}",
            line=line
        )
        self.user_message = message


def set_error_language(language: ErrorLanguage) -> None:
    """Set global error message language preference.
    
    Args:
        language: Language enum value (ENGLISH, HINDI, or BILINGUAL)
        
    Example:
        >>> set_error_language(ErrorLanguage.HINDI)
        >>> # All subsequent errors will be in Hindi only
    """
    global ERROR_LANGUAGE
    ERROR_LANGUAGE = language


def get_error_language() -> ErrorLanguage:
    """Get current error message language setting.
    
    Returns:
        Current ErrorLanguage setting
    """
    return ERROR_LANGUAGE
