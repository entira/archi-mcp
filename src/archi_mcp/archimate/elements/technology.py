"""Technology layer ArchiMate elements."""

from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class TechnologyElement(ArchiMateElement):
    """Base class for Technology layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.TECHNOLOGY
    
    @classmethod
    def create_node(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Node element."""
        return cls(
            id=id,
            name=name,
            element_type="Node",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_device(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Device element."""
        return cls(
            id=id,
            name=name,
            element_type="Device",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_system_software(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a System Software element."""
        return cls(
            id=id,
            name=name,
            element_type="System_Software",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_component(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Component element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Component",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_collaboration(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Collaboration element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Collaboration",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_interface(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Interface element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Interface",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_path(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Path element."""
        return cls(
            id=id,
            name=name,
            element_type="Path",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_communication_network(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Communication Network element."""
        return cls(
            id=id,
            name=name,
            element_type="Communication_Network",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_function(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Function element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Function",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_process(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Process element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Process",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_interaction(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Interaction element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Interaction",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_event(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Event element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Event",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_technology_service(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create a Technology Service element."""
        return cls(
            id=id,
            name=name,
            element_type="Technology_Service",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_artifact(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "TechnologyElement":
        """Create an Artifact element."""
        return cls(
            id=id,
            name=name,
            element_type="Artifact",
            layer=ArchiMateLayer.TECHNOLOGY,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )