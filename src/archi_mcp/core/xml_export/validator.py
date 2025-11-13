"""ArchiMate XML Exchange Format Validator

Validates ArchiMate XML files against the Open Group schema.
Provides validation functionality for XML export testing.
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """XML validation error."""
    pass


class ArchiMateXMLValidator:
    """
    ArchiMate XML Exchange Format Validator
    
    Validates XML files against ArchiMate 3.0 schema.
    This is a modular component for quality assurance.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self.schema = None
        
    def validate_xml_string(self, xml_string: str) -> List[str]:
        """
        Validate XML string for basic well-formedness and structure.
        
        Args:
            xml_string: XML content to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            # Parse XML
            if LXML_AVAILABLE:
                doc = etree.fromstring(xml_string.encode('utf-8'))
            else:
                doc = etree.fromstring(xml_string)
            
            # Basic structure validation
            errors.extend(self._validate_basic_structure(doc))
            
        except etree.XMLSyntaxError as e:
            errors.append(f"XML Syntax Error: {e}")
        except Exception as e:
            errors.append(f"Validation Error: {e}")
            
        return errors
    
    def validate_xml_file(self, file_path: Path) -> List[str]:
        """
        Validate XML file.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            xml_content = file_path.read_text(encoding='utf-8')
            return self.validate_xml_string(xml_content)
        except Exception as e:
            return [f"File read error: {e}"]
    
    def _validate_basic_structure(self, root: etree.Element) -> List[str]:
        """Validate basic ArchiMate XML structure."""
        errors = []
        
        # Check root element
        if root.tag != "{http://www.opengroup.org/xsd/archimate/3.0/}model":
            if not root.tag.endswith("}model") and root.tag != "model":
                errors.append("Root element must be 'model'")
        
        # Check required attributes
        if 'identifier' not in root.attrib:
            errors.append("Model element must have 'identifier' attribute")
        
        # Check for required child elements
        required_children = {'name', 'elements', 'relationships'}
        actual_children = set()
        
        for child in root:
            tag = child.tag
            # Remove namespace prefix if present
            if '}' in tag:
                tag = tag.split('}')[-1]
            actual_children.add(tag)
        
        missing_children = required_children - actual_children
        if missing_children:
            errors.append(f"Missing required child elements: {', '.join(missing_children)}")
        
        # Validate elements section
        elements_elem = self._find_child(root, 'elements')
        if elements_elem is not None:
            errors.extend(self._validate_elements_section(elements_elem))
        
        # Validate relationships section
        relationships_elem = self._find_child(root, 'relationships')  
        if relationships_elem is not None:
            errors.extend(self._validate_relationships_section(relationships_elem))
        
        return errors
    
    def _validate_elements_section(self, elements_elem: etree.Element) -> List[str]:
        """Validate elements section."""
        errors = []
        element_ids = set()
        
        for element in elements_elem:
            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            
            if tag != 'element':
                errors.append(f"Invalid child element in elements section: {tag}")
                continue
            
            # Check required attributes
            if 'identifier' not in element.attrib:
                errors.append("Element must have 'identifier' attribute")
                continue
            
            element_id = element.attrib['identifier']
            
            # Check for duplicate IDs
            if element_id in element_ids:
                errors.append(f"Duplicate element identifier: {element_id}")
            element_ids.add(element_id)
            
            # Check for xsi:type
            xsi_type_attr = None
            for attr_name in element.attrib:
                if attr_name.endswith('}type') or attr_name == 'type':
                    xsi_type_attr = element.attrib[attr_name]
                    break
            
            if not xsi_type_attr:
                errors.append(f"Element {element_id} must have xsi:type attribute")
            
            # Check for name element
            name_elem = self._find_child(element, 'name')
            if name_elem is None:
                errors.append(f"Element {element_id} must have 'name' child element")
        
        return errors
    
    def _validate_relationships_section(self, relationships_elem: etree.Element) -> List[str]:
        """Validate relationships section."""
        errors = []
        relationship_ids = set()
        
        for relationship in relationships_elem:
            tag = relationship.tag.split('}')[-1] if '}' in relationship.tag else relationship.tag
            
            if tag != 'relationship':
                errors.append(f"Invalid child element in relationships section: {tag}")
                continue
            
            # Check required attributes
            required_attrs = ['identifier', 'source', 'target']
            for attr in required_attrs:
                if attr not in relationship.attrib:
                    errors.append(f"Relationship must have '{attr}' attribute")
                    continue
            
            relationship_id = relationship.attrib.get('identifier')
            if relationship_id:
                # Check for duplicate IDs
                if relationship_id in relationship_ids:
                    errors.append(f"Duplicate relationship identifier: {relationship_id}")
                relationship_ids.add(relationship_id)
            
            # Check for xsi:type
            xsi_type_attr = None
            for attr_name in relationship.attrib:
                if attr_name.endswith('}type') or attr_name == 'type':
                    xsi_type_attr = relationship.attrib[attr_name]
                    break
            
            if not xsi_type_attr:
                errors.append(f"Relationship {relationship_id} must have xsi:type attribute")
        
        return errors
    
    def _find_child(self, parent: etree.Element, child_name: str) -> Optional[etree.Element]:
        """Find child element by name (namespace-aware)."""
        for child in parent:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == child_name:
                return child
        return None
    
    def get_validation_summary(self, errors: List[str]) -> Dict[str, Any]:
        """
        Get validation summary.
        
        Args:
            errors: List of validation errors
            
        Returns:
            Validation summary dictionary
        """
        return {
            'is_valid': len(errors) == 0,
            'error_count': len(errors),
            'errors': errors,
            'validator': 'ArchiMate XML Exchange Validator v1.0'
        }