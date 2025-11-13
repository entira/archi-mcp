"""Application layer ArchiMate elements."""

from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class ApplicationElement(ArchiMateElement):
    """Base class for Application layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.APPLICATION
    
    @classmethod
    def create_application_component(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Component element."""
        return cls(
            id=id,
            name=name,
            element_type="Component",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_collaboration(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Collaboration element."""
        return cls(
            id=id,
            name=name,
            element_type="Collaboration",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_interface(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Interface element."""
        return cls(
            id=id,
            name=name,
            element_type="Interface",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_function(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Function element."""
        return cls(
            id=id,
            name=name,
            element_type="Function",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_interaction(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Interaction element."""
        return cls(
            id=id,
            name=name,
            element_type="Interaction",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_process(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Process element."""
        return cls(
            id=id,
            name=name,
            element_type="Process",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_event(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Event element."""
        return cls(
            id=id,
            name=name,
            element_type="Event",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_application_service(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create an Application Service element."""
        return cls(
            id=id,
            name=name,
            element_type="Service",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_data_object(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "ApplicationElement":
        """Create a Data Object element."""
        return cls(
            id=id,
            name=name,
            element_type="DataObject",
            layer=ArchiMateLayer.APPLICATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )