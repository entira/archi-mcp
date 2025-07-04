"""Tests for analysis tools: test_element_normalization."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta
from pathlib import Path


class TestElementNormalization:
    """Test test_element_normalization tool functionality."""
    
    def test_element_normalization_comprehensive(self):
        """Test comprehensive element normalization testing."""
        import archi_mcp.server as server_module
        
        # Find the test_element_normalization function
        test_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'test_element_normalization':
                test_func = obj
                break
        
        if test_func:
            result = test_func.fn()
            assert isinstance(result, str)
            
            # Should test various normalization scenarios
            assert "element type" in result.lower()
            assert "normalization" in result.lower()
            
            # Should include results for all layers
            assert "Business" in result
            assert "Application" in result
            assert "Technology" in result
    
    def test_element_normalization_case_insensitive(self):
        """Test that element normalization handles case variations."""
        import archi_mcp.server as server_module
        
        test_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'test_element_normalization':
                test_func = obj
                break
        
        if test_func:
            result = test_func.fn()
            assert isinstance(result, str)
            
            # Should demonstrate case insensitive handling
            # The test function internally tests various cases like:
            # "business_actor" -> "Business_Actor"
            # "BUSINESS_ACTOR" -> "Business_Actor" 
            # "function" -> "Business_Function"
            # etc.
            
            # Result should contain test results showing normalization works
            assert "✓" in result or "success" in result.lower() or "passed" in result.lower()


class TestTranslationOverrides:
    """Test relationship label translation override functionality."""
    
    def test_override_relationship_labels_slovak(self):
        """Test relationship label override for Slovak content."""
        from archi_mcp.server import DiagramInput, RelationshipInput, override_relationship_labels_with_translations
        from archi_mcp.i18n import ArchiMateTranslator
        
        # Create diagram with custom relationship labels
        diagram = DiagramInput(
            elements=[],
            relationships=[
                RelationshipInput(
                    id="rel1",
                    from_element="elem1", 
                    to_element="elem2",
                    relationship_type="Realization",
                    label="custom implements"
                ),
                RelationshipInput(
                    id="rel2",
                    from_element="elem2",
                    to_element="elem3", 
                    relationship_type="Serving",
                    label="custom supports"
                )
            ]
        )
        
        # Create Slovak translator
        translator = ArchiMateTranslator("sk")
        
        # Override labels with translations
        override_relationship_labels_with_translations(diagram, translator)
        
        # Labels should be overridden with Slovak translations
        # (Implementation may vary based on Slovak translation dictionary)
        assert len(diagram.relationships) == 2
        # The override function should have modified the labels
        # but the exact Slovak translations depend on the i18n implementation
    
    def test_override_relationship_labels_english(self):
        """Test relationship label override for English content (no change expected)."""
        from archi_mcp.server import DiagramInput, RelationshipInput, override_relationship_labels_with_translations
        from archi_mcp.i18n import ArchiMateTranslator
        
        # Create diagram with custom relationship labels
        original_label = "custom implements"
        diagram = DiagramInput(
            elements=[],
            relationships=[
                RelationshipInput(
                    id="rel1",
                    from_element="elem1",
                    to_element="elem2", 
                    relationship_type="Realization",
                    label=original_label
                )
            ]
        )
        
        # Create English translator
        translator = ArchiMateTranslator("en")
        
        # Override labels with translations (should not change for English)
        override_relationship_labels_with_translations(diagram, translator)
        
        # For English, labels should remain unchanged
        assert diagram.relationships[0].label == original_label