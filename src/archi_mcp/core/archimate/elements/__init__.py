"""ArchiMate element definitions."""

from .base import ArchiMateElement
from .business import BusinessElement
from .application import ApplicationElement
from .technology import TechnologyElement
from .physical import PhysicalElement
from .motivation import MotivationElement
from .strategy import StrategyElement
from .implementation import ImplementationElement

# Registry of all ArchiMate elements
ARCHIMATE_ELEMENTS = {
    # Business Layer
    "Business_Actor": BusinessElement,
    "Business_Role": BusinessElement,
    "Business_Collaboration": BusinessElement,
    "Business_Interface": BusinessElement,
    "Business_Function": BusinessElement,
    "Business_Process": BusinessElement,
    "Business_Event": BusinessElement,
    "Business_Service": BusinessElement,
    "Business_Object": BusinessElement,
    "Business_Contract": BusinessElement,
    "Business_Representation": BusinessElement,
    "Location": BusinessElement,
    
    # Application Layer
    "Application_Component": ApplicationElement,
    "Application_Collaboration": ApplicationElement,
    "Application_Interface": ApplicationElement,
    "Application_Function": ApplicationElement,
    "Application_Interaction": ApplicationElement,
    "Application_Process": ApplicationElement,
    "Application_Event": ApplicationElement,
    "Application_Service": ApplicationElement,
    "Data_Object": ApplicationElement,
    "Application_DataObject": ApplicationElement,
    
    # Technology Layer
    "Node": TechnologyElement,
    "Device": TechnologyElement,
    "System_Software": TechnologyElement,
    "Technology_Component": TechnologyElement,
    "Technology_Collaboration": TechnologyElement,
    "Technology_Interface": TechnologyElement,
    "Path": TechnologyElement,
    "Communication_Network": TechnologyElement,
    "Technology_Function": TechnologyElement,
    "Technology_Process": TechnologyElement,
    "Technology_Interaction": TechnologyElement,
    "Technology_Event": TechnologyElement,
    "Technology_Service": TechnologyElement,
    "Artifact": TechnologyElement,
    
    # Physical Layer
    "Equipment": PhysicalElement,
    "Facility": PhysicalElement,
    "Distribution_Network": PhysicalElement,
    "Material": PhysicalElement,
    
    # Motivation Layer
    "Stakeholder": MotivationElement,
    "Driver": MotivationElement,
    "Assessment": MotivationElement,
    "Goal": MotivationElement,
    "Outcome": MotivationElement,
    "Principle": MotivationElement,
    "Requirement": MotivationElement,
    "Constraint": MotivationElement,
    "Meaning": MotivationElement,
    "Value": MotivationElement,
    # Also include prefixed versions for normalized elements
    "Motivation_Stakeholder": MotivationElement,
    "Motivation_Driver": MotivationElement,
    "Motivation_Assessment": MotivationElement,
    "Motivation_Goal": MotivationElement,
    "Motivation_Outcome": MotivationElement,
    "Motivation_Principle": MotivationElement,
    "Motivation_Requirement": MotivationElement,
    "Motivation_Constraint": MotivationElement,
    "Motivation_Meaning": MotivationElement,
    "Motivation_Value": MotivationElement,
    
    # Strategy Layer
    "Resource": StrategyElement,
    "Capability": StrategyElement,
    "Course_of_Action": StrategyElement,
    "Value_Stream": StrategyElement,
    
    # Implementation Layer
    "Work_Package": ImplementationElement,
    "Deliverable": ImplementationElement,
    "Implementation_Event": ImplementationElement,
    "Plateau": ImplementationElement,
    "Gap": ImplementationElement,
}

__all__ = [
    "ArchiMateElement",
    "BusinessElement",
    "ApplicationElement",
    "TechnologyElement", 
    "PhysicalElement",
    "MotivationElement",
    "StrategyElement",
    "ImplementationElement",
    "ARCHIMATE_ELEMENTS",
]