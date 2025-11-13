"""Business layer ArchiMate elements."""

from typing import List
from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class BusinessElement(ArchiMateElement):
    """Base class for Business layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.BUSINESS
    
    @classmethod
    def create_business_actor(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Actor element."""
        return cls(
            id=id,
            name=name,
            element_type="Actor",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_role(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Role element."""
        return cls(
            id=id,
            name=name,
            element_type="Role",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_collaboration(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Collaboration element."""
        return cls(
            id=id,
            name=name,
            element_type="Collaboration",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_interface(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Interface element."""
        return cls(
            id=id,
            name=name,
            element_type="Interface",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_function(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Function element."""
        return cls(
            id=id,
            name=name,
            element_type="Function",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_process(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Process element."""
        return cls(
            id=id,
            name=name,
            element_type="Process",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_event(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Event element."""
        return cls(
            id=id,
            name=name,
            element_type="Event",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_service(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Service element."""
        return cls(
            id=id,
            name=name,
            element_type="Service",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_object(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Object element."""
        return cls(
            id=id,
            name=name,
            element_type="Object",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_contract(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Contract element."""
        return cls(
            id=id,
            name=name,
            element_type="Contract",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_business_representation(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Business Representation element."""
        return cls(
            id=id,
            name=name,
            element_type="Representation",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_location(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "BusinessElement":
        """Create a Location element."""
        return cls(
            id=id,
            name=name,
            element_type="Location",
            layer=ArchiMateLayer.BUSINESS,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )