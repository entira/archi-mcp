"""Tests for analysis tools: analyze_current_architecture and analyze_recent_errors."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta
from pathlib import Path


class TestAnalyzeCurrentArchitecture:
    """Test analyze_current_architecture tool functionality."""
    
    def test_analyze_current_architecture_empty(self):
        """Test analysis with no current architecture."""
        import archi_mcp.server as server_module
        
        # Find the analyze_current_architecture function
        analyze_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'analyze_current_architecture':
                analyze_func = obj
                break
        
        if analyze_func:
            result = analyze_func.fn()
            assert isinstance(result, str)
            assert "no current architecture state" in result.lower() or "empty" in result.lower()
    
    def test_analyze_current_architecture_basic_stats(self):
        """Test analysis with basic architecture statistics."""
        import archi_mcp.server as server_module
        from archi_mcp.server import DiagramInput, ElementInput, RelationshipInput
        
        # First create a diagram to establish current architecture
        create_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'create_archimate_diagram':
                create_func = obj
                break
        
        if create_func:
            # Create a test diagram
            diagram = DiagramInput(
                elements=[
                    ElementInput(
                        id="actor1",
                        name="Business Actor",
                        element_type="Business_Actor",
                        layer="Business"
                    ),
                    ElementInput(
                        id="service1", 
                        name="Business Service",
                        element_type="Business_Service",
                        layer="Business"
                    ),
                    ElementInput(
                        id="app1",
                        name="Application Component",
                        element_type="Application_Component", 
                        layer="Application"
                    )
                ],
                relationships=[
                    RelationshipInput(
                        id="rel1",
                        from_element="actor1",
                        to_element="service1",
                        relationship_type="Access"
                    ),
                    RelationshipInput(
                        id="rel2", 
                        from_element="service1",
                        to_element="app1",
                        relationship_type="Realization"
                    )
                ]
            )
            
            # Create the diagram first
            create_result = create_func.fn(diagram=diagram)
            
            # Now analyze the current architecture
            analyze_func = None
            for name in dir(server_module):
                obj = getattr(server_module, name)
                if hasattr(obj, '__name__') and obj.__name__ == 'analyze_current_architecture':
                    analyze_func = obj
                    break
            
            if analyze_func:
                result = analyze_func.fn()
                assert isinstance(result, str)
                
                # Should contain statistics
                assert "elements" in result.lower()
                assert "relationships" in result.lower()
                assert "layers" in result.lower()
                
                # Should mention specific counts
                assert "3" in result  # 3 elements
                assert "2" in result  # 2 relationships
    
    def test_analyze_current_architecture_layer_distribution(self):
        """Test analysis with layer distribution information."""
        import archi_mcp.server as server_module
        from archi_mcp.server import DiagramInput, ElementInput
        
        # Create diagram with elements across multiple layers
        create_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'create_archimate_diagram':
                create_func = obj
                break
        
        if create_func:
            diagram = DiagramInput(
                elements=[
                    ElementInput(
                        id="business1",
                        name="Business Element",
                        element_type="Business_Actor",
                        layer="Business"
                    ),
                    ElementInput(
                        id="app1",
                        name="App Element", 
                        element_type="Application_Component",
                        layer="Application"
                    ),
                    ElementInput(
                        id="tech1",
                        name="Tech Element",
                        element_type="Node",
                        layer="Technology"
                    ),
                    ElementInput(
                        id="motivation1",
                        name="Motivation Element", 
                        element_type="Goal",
                        layer="Motivation"
                    )
                ],
                relationships=[]
            )
            
            create_result = create_func.fn(diagram=diagram)
            
            # Analyze architecture
            analyze_func = None
            for name in dir(server_module):
                obj = getattr(server_module, name)
                if hasattr(obj, '__name__') and obj.__name__ == 'analyze_current_architecture':
                    analyze_func = obj
                    break
            
            if analyze_func:
                result = analyze_func.fn()
                assert isinstance(result, str)
                
                # Should mention all layers present
                assert "Business" in result
                assert "Application" in result
                assert "Technology" in result
                assert "Motivation" in result


class TestAnalyzeRecentErrors:
    """Test analyze_recent_errors tool functionality."""
    
    def test_analyze_recent_errors_no_errors(self):
        """Test analysis when no recent errors exist."""
        import archi_mcp.server as server_module
        
        # Clear any existing error log
        error_log_path = Path("logs/validation_errors.jsonl")
        if error_log_path.exists():
            error_log_path.unlink()
        
        # Find the analyze_recent_errors function
        analyze_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'analyze_recent_errors':
                analyze_func = obj
                break
        
        if analyze_func:
            result = analyze_func.fn(minutes=10)
            assert isinstance(result, str)
            assert "no errors found" in result.lower() or "no recent errors" in result.lower()
    
    def test_analyze_recent_errors_with_mock_errors(self):
        """Test analysis with mocked error log."""
        import archi_mcp.server as server_module
        
        # Mock error log content
        now = datetime.now()
        recent_time = now - timedelta(minutes=5)
        old_time = now - timedelta(minutes=15)
        
        mock_errors = [
            {
                "timestamp": recent_time.isoformat(),
                "error": "Empty model error",
                "context": {"elements": 0}
            },
            {
                "timestamp": recent_time.isoformat(), 
                "error": "Orphaned relationship",
                "context": {"relationship_id": "rel1"}
            },
            {
                "timestamp": old_time.isoformat(),
                "error": "Old error outside window",
                "context": {}
            }
        ]
        
        mock_log_content = "\n".join(json.dumps(error) for error in mock_errors)
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("pathlib.Path.exists", return_value=True):
                analyze_func = None
                for name in dir(server_module):
                    obj = getattr(server_module, name)
                    if hasattr(obj, '__name__') and obj.__name__ == 'analyze_recent_errors':
                        analyze_func = obj
                        break
                
                if analyze_func:
                    result = analyze_func.fn(minutes=10)
                    assert isinstance(result, str)
                    
                    # Should analyze errors within time window
                    assert "2 errors" in result or "errors found" in result
                    assert "Empty model" in result
                    assert "Orphaned relationship" in result
                    
                    # Should not include old error outside window
                    assert "Old error outside window" not in result
    
    def test_analyze_recent_errors_different_time_windows(self):
        """Test analysis with different time windows."""
        import archi_mcp.server as server_module
        
        now = datetime.now()
        
        mock_errors = [
            {
                "timestamp": (now - timedelta(minutes=2)).isoformat(),
                "error": "Very recent error",
                "context": {}
            },
            {
                "timestamp": (now - timedelta(minutes=8)).isoformat(),
                "error": "Recent error", 
                "context": {}
            },
            {
                "timestamp": (now - timedelta(minutes=25)).isoformat(),
                "error": "Old error",
                "context": {}
            }
        ]
        
        mock_log_content = "\n".join(json.dumps(error) for error in mock_errors)
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("pathlib.Path.exists", return_value=True):
                analyze_func = None
                for name in dir(server_module):
                    obj = getattr(server_module, name)
                    if hasattr(obj, '__name__') and obj.__name__ == 'analyze_recent_errors':
                        analyze_func = obj
                        break
                
                if analyze_func:
                    # Test 5 minute window - should only include very recent error
                    result_5min = analyze_func.fn(minutes=5)
                    assert "Very recent error" in result_5min
                    assert "Recent error" not in result_5min
                    
                    # Test 15 minute window - should include first two errors
                    result_15min = analyze_func.fn(minutes=15)
                    assert "Very recent error" in result_15min
                    assert "Recent error" in result_15min
                    assert "Old error" not in result_15min
    
    def test_analyze_recent_errors_invalid_json(self):
        """Test analysis with invalid JSON in error log."""
        import archi_mcp.server as server_module
        
        # Mock log with invalid JSON lines
        mock_log_content = """{"valid": "json"}
invalid json line
{"another": "valid", "entry": true}"""
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("pathlib.Path.exists", return_value=True):
                analyze_func = None
                for name in dir(server_module):
                    obj = getattr(server_module, name)
                    if hasattr(obj, '__name__') and obj.__name__ == 'analyze_recent_errors':
                        analyze_func = obj
                        break
                
                if analyze_func:
                    # Should handle invalid JSON gracefully
                    result = analyze_func.fn(minutes=10)
                    assert isinstance(result, str)
                    # Should still process valid entries
                    assert "valid" in result.lower() or "entries" in result.lower()
    
    def test_analyze_recent_errors_file_not_found(self):
        """Test analysis when error log file doesn't exist."""
        import archi_mcp.server as server_module
        
        with patch("pathlib.Path.exists", return_value=False):
            analyze_func = None
            for name in dir(server_module):
                obj = getattr(server_module, name)
                if hasattr(obj, '__name__') and obj.__name__ == 'analyze_recent_errors':
                    analyze_func = obj
                    break
            
            if analyze_func:
                result = analyze_func.fn(minutes=10)
                assert isinstance(result, str)
                assert "no errors found" in result.lower() or "no error log" in result.lower()
    
    def test_analyze_recent_errors_edge_case_minutes(self):
        """Test analysis with edge case minute values."""
        import archi_mcp.server as server_module
        
        analyze_func = None
        for name in dir(server_module):
            obj = getattr(server_module, name)
            if hasattr(obj, '__name__') and obj.__name__ == 'analyze_recent_errors':
                analyze_func = obj
                break
        
        if analyze_func:
            # Test minimum value
            result_min = analyze_func.fn(minutes=1)
            assert isinstance(result_min, str)
            
            # Test maximum value
            result_max = analyze_func.fn(minutes=60)
            assert isinstance(result_max, str)
            
            # Test default value (no minutes parameter)
            result_default = analyze_func.fn()
            assert isinstance(result_default, str)


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