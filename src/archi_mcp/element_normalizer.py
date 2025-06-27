"""Element type normalizer for proper ArchiMate syntax."""

def normalize_element_type(element_type: str) -> str:
    """
    Normalize element type to proper ArchiMate PlantUML syntax.
    Fixes common issues like kebab-case, missing prefixes, etc.
    """
    # Handle kebab-case to underscore conversion
    normalized = element_type.replace('-', '_')
    
    # Common mappings for element types
    type_mappings = {
        # Business layer
        'business_actor': 'Business_Actor',
        'business_process': 'Business_Process', 
        'business_service': 'Business_Service',
        'business_object': 'Business_Object',
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
        'application_service': 'Application_Service',
        'application_collaboration': 'Application_Collaboration',
        'application_interface': 'Application_Interface',
        'application_function': 'Application_Function',
        'application_interaction': 'Application_Interaction',
        'application_process': 'Application_Process',
        'application_event': 'Application_Event',
        'data_object': 'Application_DataObject',
        'application_dataobject': 'Application_DataObject',
        'artifact': 'Application_Artifact',
        
        # Technology layer  
        'node': 'Technology_Node',
        'device': 'Technology_Device',
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
        'driver': 'Motivation_Driver',
        'assessment': 'Motivation_Assessment',
        'goal': 'Motivation_Goal',
        'outcome': 'Motivation_Outcome',
        'principle': 'Motivation_Principle',
        'requirement': 'Motivation_Requirement',
        'constraint': 'Motivation_Constraint',
        'meaning': 'Motivation_Meaning',
        'value': 'Motivation_Value',
        
        # Strategy layer
        'resource': 'Strategy_Resource',
        'capability': 'Strategy_Capability',
        'value_stream': 'Strategy_Value_Stream',
        'course_of_action': 'Strategy_Course_of_Action',
        
        # Implementation layer
        'work_package': 'Implementation_Work_Package',
        'deliverable': 'Implementation_Deliverable',
        'implementation_event': 'Implementation_Event',
        'plateau': 'Implementation_Plateau',
        'gap': 'Implementation_Gap'
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