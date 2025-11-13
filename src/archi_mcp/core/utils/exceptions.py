"""Custom exceptions for ArchiMate MCP server."""

from typing import Any, Dict, Optional


class ArchiMateError(Exception):
    """Base exception for ArchiMate-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ArchiMateValidationError(ArchiMateError):
    """Exception raised when ArchiMate model validation fails."""
    
    def __init__(
        self,
        message: str,
        element_id: Optional[str] = None,
        element_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.element_id = element_id
        self.element_type = element_type


class ArchiMateRelationshipError(ArchiMateError):
    """Exception raised when relationship creation or validation fails."""
    
    def __init__(
        self,
        message: str,
        from_element: Optional[str] = None,
        to_element: Optional[str] = None,
        relationship_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.from_element = from_element
        self.to_element = to_element
        self.relationship_type = relationship_type


class ArchiMateGenerationError(ArchiMateError):
    """Exception raised when PlantUML code generation fails."""
    pass


class ArchiMateTemplateError(ArchiMateError):
    """Exception raised when template processing fails."""
    
    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.template_name = template_name
        self.template_type = template_type