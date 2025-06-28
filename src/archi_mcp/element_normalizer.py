"""Element type normalizer for proper ArchiMate syntax."""

def normalize_element_type(element_type: str, layer: str = None) -> str:
    """
    Normalize element type to proper ArchiMate PlantUML syntax.
    Fixes common issues like kebab-case, missing prefixes, etc.
    For PlantUML output, adds layer prefixes for ambiguous elements.
    """
    # Handle kebab-case to underscore conversion
    normalized = element_type.replace('-', '_')
    
    # Common mappings for element types
    type_mappings = {
        # Business layer
        'business_actor': 'Business_Actor',
        'actor': 'Business_Actor',  # Short version
        'business_process': 'Business_Process',
        'process': 'Business_Process',  # Short version
        'business_service': 'Business_Service',
        'business_object': 'Business_Object',
        'object': 'Business_Object',  # Short version
        'business_role': 'Business_Role',
        'business_collaboration': 'Business_Collaboration',
        'business_interface': 'Business_Interface',
        'business_event': 'Business_Event',
        'business_function': 'Business_Function',
        'business_interaction': 'Business_Interaction',
        'business_contract': 'Business_Contract',
        'business_representation': 'Business_Representation',
        
        # Application layer
        'application_component': 'Application_Component',
        'component': 'Application_Component',  # Short version
        'application_service': 'Application_Service',
        'application_collaboration': 'Application_Collaboration',
        'application_interface': 'Application_Interface',
        'application_function': 'Application_Function',
        'application_interaction': 'Application_Interaction',
        'application_process': 'Application_Process',
        'application_event': 'Application_Event',
        'data_object': 'Application_DataObject',  # Fixed: Use Application_DataObject for consistency
        'dataobject': 'Application_DataObject',  # Short version
        'application_dataobject': 'Application_DataObject',
        'artifact': 'Application_Artifact',
        
        # Technology layer  
        'node': 'Technology_Node',
        'technology_node': 'Technology_Node',
        'device': 'Technology_Device',
        'technology_device': 'Technology_Device',
        'system_software': 'Technology_SystemSoftware',
        'technology_systemsoftware': 'Technology_SystemSoftware',
        'technology_collaboration': 'Technology_Collaboration',
        'technology_interface': 'Technology_Interface',
        'technology_service': 'Technology_Service',
        'technology_function': 'Technology_Function',
        'technology_process': 'Technology_Process',
        'technology_interaction': 'Technology_Interaction',
        'technology_event': 'Technology_Event',
        'path': 'Technology_Path',
        'communication_network': 'Technology_Communication_Network',
        'network': 'Technology_Communication_Network',
        
        # Physical layer
        'equipment': 'Physical_Equipment',
        'facility': 'Physical_Facility', 
        'distribution_network': 'Physical_Distribution_Network',
        'material': 'Physical_Material',
        
        # Motivation layer
        'stakeholder': 'Motivation_Stakeholder',
        'motivation_stakeholder': 'Motivation_Stakeholder',
        'driver': 'Motivation_Driver',
        'motivation_driver': 'Motivation_Driver',
        'assessment': 'Motivation_Assessment',
        'motivation_assessment': 'Motivation_Assessment',
        'goal': 'Motivation_Goal',
        'motivation_goal': 'Motivation_Goal',
        'outcome': 'Motivation_Outcome',
        'motivation_outcome': 'Motivation_Outcome',
        'principle': 'Motivation_Principle',
        'motivation_principle': 'Motivation_Principle',
        'requirement': 'Motivation_Requirement',
        'motivation_requirement': 'Motivation_Requirement',
        'constraint': 'Motivation_Constraint',
        'motivation_constraint': 'Motivation_Constraint',
        'meaning': 'Motivation_Meaning',
        'motivation_meaning': 'Motivation_Meaning',
        'value': 'Motivation_Value',
        'motivation_value': 'Motivation_Value',
        
        # Strategy layer
        'resource': 'Strategy_Resource',
        'capability': 'Strategy_Capability',
        'value_stream': 'Strategy_Value_Stream',
        'course_of_action': 'Strategy_Course_of_Action',
        
        # Implementation layer
        'work_package': 'Implementation_Work_Package',
        'workpackage': 'Implementation_Work_Package',  # Short version  
        'implementation_work_package': 'Implementation_Work_Package',
        'deliverable': 'Implementation_Deliverable',
        'implementation_deliverable': 'Implementation_Deliverable',
        'implementation_event': 'Implementation_Event',
        'plateau': 'Implementation_Plateau',
        'implementation_plateau': 'Implementation_Plateau',
        'gap': 'Implementation_Gap',
        'implementation_gap': 'Implementation_Gap'
    }
    
    # Try exact match first
    if normalized.lower() in type_mappings:
        return type_mappings[normalized.lower()]
    
    # Try without layer prefix
    base_type = normalized.lower()
    for prefix in ['business_', 'application_', 'technology_', 'physical_', 'motivation_', 'strategy_', 'implementation_']:
        if base_type.startswith(prefix):
            base_type = base_type[len(prefix):]
            break
    
    if base_type in type_mappings:
        return type_mappings[base_type]
    
    # If no mapping found, try to construct proper format
    parts = normalized.split('_')
    if len(parts) >= 2:
        # Capitalize each part
        formatted_parts = [part.capitalize() for part in parts]
        return '_'.join(formatted_parts)
    
    # Last resort - capitalize first letter
    return normalized.capitalize()

def normalize_for_plantuml(element_type: str, layer: str) -> str:
    """
    Normalize element type specifically for PlantUML output.
    Adds layer prefixes for elements that need them to avoid ambiguity in PlantUML.
    """
    # First do basic normalization
    normalized = normalize_element_type(element_type)
    
    # Elements that need layer prefixes based on context
    layer_specific_mappings = {
        'motivation': {
            'Stakeholder': 'Motivation_Stakeholder',
            'Driver': 'Motivation_Driver', 
            'Assessment': 'Motivation_Assessment',
            'Goal': 'Motivation_Goal',
            'Outcome': 'Motivation_Outcome',
            'Principle': 'Motivation_Principle',
            'Requirement': 'Motivation_Requirement',
            'Constraint': 'Motivation_Constraint',
            'Meaning': 'Motivation_Meaning',
            'Value': 'Motivation_Value',
        },
        'business': {
            'Actor': 'Business_Actor',
            'Service': 'Business_Service', 
            'Process': 'Business_Process',
            'Object': 'Business_Object',
        },
        'application': {
            'Component': 'Application_Component',
            'Service': 'Application_Service',
            'DataObject': 'Application_DataObject',  # Fixed: Use Application_DataObject for consistency
        },
        'technology': {
            'Service': 'Technology_Service',
        },
        'implementation': {
            'Work_Package': 'Implementation_Work_Package',
            'Workpackage': 'Implementation_Work_Package',  # Handle both forms
            'WorkPackage': 'Implementation_Work_Package',   # Handle CamelCase
            'Deliverable': 'Implementation_Deliverable',
            'Gap': 'Implementation_Gap',
            'Plateau': 'Implementation_Plateau',
        }
    }
    
    # Check layer-specific mappings first
    layer_lower = layer.lower()
    if layer_lower in layer_specific_mappings:
        layer_mappings = layer_specific_mappings[layer_lower]
        if normalized in layer_mappings:
            return layer_mappings[normalized]
    
    # If the element already has a layer prefix, keep it
    if '_' in normalized and any(normalized.startswith(prefix) for prefix in 
                                ['Business_', 'Application_', 'Technology_', 'Physical_', 
                                 'Motivation_', 'Strategy_', 'Implementation_']):
        return normalized
    
    return normalized

def validate_element_id(element_id: str) -> str:
    """
    Validate and normalize element ID for PlantUML.
    Ensures no spaces, hyphens, or special characters.
    """
    # Replace problematic characters
    normalized_id = element_id.replace(' ', '_').replace('-', '_')
    
    # Remove other special characters except underscore
    import re
    normalized_id = re.sub(r'[^a-zA-Z0-9_]', '', normalized_id)
    
    # Ensure it doesn't start with a number
    if normalized_id and normalized_id[0].isdigit():
        normalized_id = f"elem_{normalized_id}"
    
    return normalized_id

def validate_element_name(element_name: str) -> str:
    """
    Validate element name for PlantUML.
    Ensures proper quoting for names with special characters.
    """
    # Always quote names to handle special characters
    if not element_name.startswith('"') or not element_name.endswith('"'):
        # Escape existing quotes
        escaped_name = element_name.replace('"', '\\"')
        return f'"{escaped_name}"'
    
    return element_name