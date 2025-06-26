"""Physical layer ArchiMate elements."""

from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class PhysicalElement(ArchiMateElement):
    """Base class for Physical layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.PHYSICAL
    
    @classmethod
    def create_equipment(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "PhysicalElement":
        """Create an Equipment element."""
        return cls(
            id=id,
            name=name,
            element_type="Equipment",
            layer=ArchiMateLayer.PHYSICAL,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_facility(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "PhysicalElement":
        """Create a Facility element."""
        return cls(
            id=id,
            name=name,
            element_type="Facility",
            layer=ArchiMateLayer.PHYSICAL,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_distribution_network(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "PhysicalElement":
        """Create a Distribution Network element."""
        return cls(
            id=id,
            name=name,
            element_type="Distribution_Network",
            layer=ArchiMateLayer.PHYSICAL,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_material(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "PhysicalElement":
        """Create a Material element."""
        return cls(
            id=id,
            name=name,
            element_type="Material",
            layer=ArchiMateLayer.PHYSICAL,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )