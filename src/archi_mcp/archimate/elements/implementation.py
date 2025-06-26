"""Implementation layer ArchiMate elements."""

from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class ImplementationElement(ArchiMateElement):
    """Base class for Implementation layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.IMPLEMENTATION
    
    @classmethod
    def create_work_package(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ImplementationElement":
        """Create a Work Package element."""
        return cls(
            id=id,
            name=name,
            element_type="Work_Package",
            layer=ArchiMateLayer.IMPLEMENTATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_deliverable(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ImplementationElement":
        """Create a Deliverable element."""
        return cls(
            id=id,
            name=name,
            element_type="Deliverable",
            layer=ArchiMateLayer.IMPLEMENTATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_implementation_event(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ImplementationElement":
        """Create an Implementation Event element."""
        return cls(
            id=id,
            name=name,
            element_type="Implementation_Event",
            layer=ArchiMateLayer.IMPLEMENTATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_plateau(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ImplementationElement":
        """Create a Plateau element."""
        return cls(
            id=id,
            name=name,
            element_type="Plateau",
            layer=ArchiMateLayer.IMPLEMENTATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_gap(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ImplementationElement":
        """Create a Gap element."""
        return cls(
            id=id,
            name=name,
            element_type="Gap",
            layer=ArchiMateLayer.IMPLEMENTATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )