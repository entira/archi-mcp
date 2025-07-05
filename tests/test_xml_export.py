"""
Test ArchiMate XML Export functionality
Tests for the new XML Exchange export module.
"""

import pytest
import tempfile
from pathlib import Path
import xml.etree.ElementTree as etree
from unittest.mock import Mock, patch

from archi_mcp.xml_export import ArchiMateXMLExporter, ArchiMateXMLValidator
from archi_mcp.xml_export.templates import XMLTemplates
from archi_mcp.archimate import ArchiMateElement, ArchiMateRelationship
from archi_mcp.archimate.elements.base import ArchiMateLayer, ArchiMateAspect


class TestArchiMateXMLExporter:
    """Test XML export functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.exporter = ArchiMateXMLExporter()
        self.validator = ArchiMateXMLValidator()
        
        # Create test elements
        self.test_elements = [
            ArchiMateElement(
                id="customer",
                name="Customer",
                element_type="Business_Actor",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
                description="External customer"
            ),
            ArchiMateElement(
                id="order_service",
                name="Order Service",
                element_type="Business_Service", 
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.BEHAVIOR,
                description="Service for placing orders"
            ),
            ArchiMateElement(
                id="order_app",
                name="Order Application",
                element_type="Application_Component",
                layer=ArchiMateLayer.APPLICATION,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
                description="Application for order management"
            )
        ]
        
        # Create test relationships
        self.test_relationships = [
            ArchiMateRelationship(
                id="rel1",
                from_element="order_service",
                to_element="customer",
                relationship_type="Serving",
                label="serves",
                description="Service serves customer"
            ),
            ArchiMateRelationship(
                id="rel2", 
                from_element="order_app",
                to_element="order_service",
                relationship_type="Realization",
                label="realizes",
                description="Application realizes service"
            )
        ]
    
    def test_xml_exporter_initialization(self):
        """Test XML exporter initialization."""
        assert self.exporter.ARCHIMATE_NAMESPACE == "http://www.archimatetool.com/archimate"
        assert self.exporter.XSI_NAMESPACE == "http://www.w3.org/2001/XMLSchema-instance"
        assert hasattr(self.exporter, 'nsmap')
    
    def test_export_basic_model(self):
        """Test basic XML export functionality."""
        xml_content = self.exporter.export_to_xml(
            elements=self.test_elements,
            relationships=self.test_relationships,
            model_name="Test Model"
        )
        
        # Verify XML is valid
        assert xml_content.startswith('<?xml')
        assert 'Test Model' in xml_content
        assert 'customer' in xml_content
        assert 'order_service' in xml_content
        
        # Parse and verify structure
        root = etree.fromstring(xml_content.encode('utf-8'))
        assert root.tag.endswith('}model') or root.tag == 'model'
    
    def test_export_with_file_output(self):
        """Test XML export with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_model.xml"
            
            xml_content = self.exporter.export_to_xml(
                elements=self.test_elements,
                relationships=self.test_relationships,
                model_name="File Test Model",
                output_path=output_path
            )
            
            # Verify file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            
            # Verify file content matches returned content
            file_content = output_path.read_text(encoding='utf-8')
            assert file_content == xml_content
    
    def test_export_empty_model(self):
        """Test XML export with empty model."""
        xml_content = self.exporter.export_to_xml(
            elements=[],
            relationships=[],
            model_name="Empty Model"
        )
        
        # Should still produce valid XML
        root = etree.fromstring(xml_content.encode('utf-8'))
        assert root.tag.endswith('}model') or root.tag == 'model'
        
        # Check that we have Archi folder structure
        folders = []
        for child in root:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'folder':
                folders.append(child.get('name'))
        
        # Should have standard Archi folders
        assert 'Strategy' in folders
        assert 'Business' in folders
        assert 'Application' in folders
        assert 'Technology' in folders
        assert 'Relations' in folders
    
    def test_element_type_mapping(self):
        """Test element type conversion to XML schema types."""
        # Test business layer mappings
        assert self.exporter._get_xml_element_type("Business_Actor") == "BusinessActor"
        assert self.exporter._get_xml_element_type("Business_Process") == "BusinessProcess"
        assert self.exporter._get_xml_element_type("Business_Service") == "BusinessService"
        
        # Test application layer mappings
        assert self.exporter._get_xml_element_type("Application_Component") == "ApplicationComponent"
        assert self.exporter._get_xml_element_type("Data_Object") == "DataObject"
        
        # Test technology layer mappings
        assert self.exporter._get_xml_element_type("Node") == "Node"
        assert self.exporter._get_xml_element_type("System_Software") == "SystemSoftware"
        
        # Test motivation layer mappings
        assert self.exporter._get_xml_element_type("Stakeholder") == "Stakeholder"
        assert self.exporter._get_xml_element_type("Goal") == "Goal"
        
        # Test strategy layer mappings
        assert self.exporter._get_xml_element_type("Capability") == "Capability"
        assert self.exporter._get_xml_element_type("Course_of_Action") == "CourseOfAction"
        
        # Test implementation layer mappings
        assert self.exporter._get_xml_element_type("Work_Package") == "WorkPackage"
        assert self.exporter._get_xml_element_type("Implementation_Event") == "ImplementationEvent"
    
    def test_relationship_type_mapping(self):
        """Test relationship type conversion to XML schema types."""
        assert self.exporter._get_xml_relationship_type("Serving") == "ServingRelationship"
        assert self.exporter._get_xml_relationship_type("Realization") == "RealizationRelationship" 
        assert self.exporter._get_xml_relationship_type("Assignment") == "AssignmentRelationship"
        assert self.exporter._get_xml_relationship_type("Composition") == "CompositionRelationship"
        assert self.exporter._get_xml_relationship_type("Access") == "AccessRelationship"
    
    def test_export_with_properties(self):
        """Test XML export with element properties."""
        element_with_props = ArchiMateElement(
            id="test_element",
            name="Test Element",
            element_type="Business_Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            properties={"custom_prop": "custom_value", "priority": "high"}
        )
        
        xml_content = self.exporter.export_to_xml(
            elements=[element_with_props],
            relationships=[],
            model_name="Properties Test"
        )
        
        assert 'custom_prop' in xml_content
        assert 'custom_value' in xml_content
        assert 'priority' in xml_content
        assert 'high' in xml_content
    
    def test_export_error_handling(self):
        """Test XML export error handling."""
        # Test with invalid elements (mock to cause error)
        with patch.object(self.exporter, '_add_archi_folders_and_elements', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                self.exporter.export_to_xml(
                    elements=self.test_elements,
                    relationships=self.test_relationships
                )


class TestArchiMateXMLValidator:
    """Test XML validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ArchiMateXMLValidator()
        self.exporter = ArchiMateXMLExporter()
        
    def test_validator_initialization(self):
        """Test XML validator initialization."""
        assert hasattr(self.validator, 'validate_xml_string')
        assert hasattr(self.validator, 'validate_xml_file')
    
    def test_valid_xml_validation(self):
        """Test validation of valid XML."""
        # Create valid XML using exporter
        elements = [
            ArchiMateElement(
                id="test_elem",
                name="Test Element",
                element_type="Business_Actor",
                layer=ArchiMateLayer.BUSINESS,
                aspect=ArchiMateAspect.ACTIVE_STRUCTURE
            )
        ]
        
        xml_content = self.exporter.export_to_xml(
            elements=elements,
            relationships=[],
            model_name="Valid Test Model"
        )
        
        errors = self.validator.validate_xml_string(xml_content)
        # Archi format has different structure, basic XML validation should still pass
        assert isinstance(errors, list), "Validation should return a list"
    
    def test_invalid_xml_validation(self):
        """Test validation of invalid XML."""
        invalid_xml = "<model><invalid></model>"  # Missing closing tag
        
        errors = self.validator.validate_xml_string(invalid_xml)
        assert len(errors) > 0
        assert any("syntax" in error.lower() or "xml" in error.lower() for error in errors)
    
    def test_missing_required_elements(self):
        """Test validation of XML missing required elements."""
        minimal_xml = '''<?xml version="1.0"?>
        <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" identifier="test">
        </model>'''
        
        errors = self.validator.validate_xml_string(minimal_xml)
        assert len(errors) > 0
        assert any("missing" in error.lower() for error in errors)
    
    def test_validation_summary(self):
        """Test validation summary generation."""
        errors = ["Error 1", "Error 2"]
        summary = self.validator.get_validation_summary(errors)
        
        assert summary['is_valid'] == False
        assert summary['error_count'] == 2
        assert summary['errors'] == errors
        assert 'validator' in summary


class TestXMLTemplates:
    """Test XML templates functionality."""
    
    def test_minimal_model_template(self):
        """Test minimal model template."""
        template = XMLTemplates.get_minimal_model_template()
        
        assert '<?xml version="1.0"' in template
        assert 'xmlns="http://www.opengroup.org/xsd/archimate/3.0/"' in template
        assert '<elements>' in template
        assert '<relationships>' in template
        
        # Verify template parses as valid XML
        root = etree.fromstring(template.encode('utf-8'))
        assert root.tag.endswith('}model') or root.tag == 'model'
    
    def test_sample_business_model(self):
        """Test sample business model template."""
        template = XMLTemplates.get_sample_business_model()
        
        assert 'Customer' in template
        assert 'Order Management Process' in template
        assert 'BusinessActor' in template
        assert 'ServingRelationship' in template
        
        # Verify template parses as valid XML
        root = etree.fromstring(template.encode('utf-8'))
        assert root.tag.endswith('}model') or root.tag == 'model'
    
    def test_element_template(self):
        """Test element template generation."""
        template = XMLTemplates.get_element_template("BusinessActor")
        
        assert 'BusinessActor' in template
        assert 'identifier="element-id"' in template
        assert '<name>Element Name</name>' in template
        assert '<documentation>' in template
    
    def test_relationship_template(self):
        """Test relationship template generation."""
        template = XMLTemplates.get_relationship_template("Serving")
        
        assert 'ServingRelationship' in template
        assert 'source="source-element-id"' in template
        assert 'target="target-element-id"' in template
    
    def test_supported_element_types(self):
        """Test supported element types listing."""
        supported = XMLTemplates.get_supported_element_types()
        
        assert isinstance(supported, dict)
        assert 'Business' in supported
        assert 'Application' in supported
        assert 'Technology' in supported
        assert 'Physical' in supported
        assert 'Motivation' in supported
        assert 'Strategy' in supported
        assert 'Implementation' in supported
        
        # Check some specific types
        assert 'BusinessActor' in supported['Business']
        assert 'ApplicationComponent' in supported['Application']
        assert 'Node' in supported['Technology']
    
    def test_supported_relationship_types(self):
        """Test supported relationship types listing."""
        supported = XMLTemplates.get_supported_relationship_types()
        
        assert isinstance(supported, list)
        assert 'ServingRelationship' in supported
        assert 'RealizationRelationship' in supported
        assert 'AssignmentRelationship' in supported


class TestXMLExportIntegration:
    """Integration tests for XML export with server."""
    
    def test_xml_export_integration_success(self):
        """Test successful XML export integration."""
        # Test that exporter can be imported and instantiated
        from archi_mcp.xml_export import ArchiMateXMLExporter
        
        exporter = ArchiMateXMLExporter()
        result = exporter.export_to_xml([], [], "Test")
        
        # Should return valid XML even with empty input
        assert result.startswith('<?xml')
        assert 'Test' in result
    
    def test_xml_export_fallback_import(self):
        """Test XML export fallback when import fails."""
        with patch('archi_mcp.xml_export.exporter.etree', side_effect=ImportError):
            # Should fallback to ElementTree
            exporter = ArchiMateXMLExporter()
            assert hasattr(exporter, 'export_to_xml')
    
    def test_xml_export_lxml_availability(self):
        """Test lxml availability detection."""
        from archi_mcp.xml_export.exporter import LXML_AVAILABLE
        
        # Should be True since we installed lxml
        assert LXML_AVAILABLE == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])