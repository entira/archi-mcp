"""Strategy layer ArchiMate elements."""

from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class StrategyElement(ArchiMateElement):
    """Base class for Strategy layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.STRATEGY
    
    @classmethod
    def create_resource(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "StrategyElement":
        """Create a Resource element."""
        return cls(
            id=id,
            name=name,
            element_type="Resource",
            layer=ArchiMateLayer.STRATEGY,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_capability(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "StrategyElement":
        """Create a Capability element."""
        return cls(
            id=id,
            name=name,
            element_type="Capability",
            layer=ArchiMateLayer.STRATEGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_course_of_action(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "StrategyElement":
        """Create a Course of Action element."""
        return cls(
            id=id,
            name=name,
            element_type="Course_of_Action",
            layer=ArchiMateLayer.STRATEGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_value_stream(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "StrategyElement":
        """Create a Value Stream element."""
        return cls(
            id=id,
            name=name,
            element_type="Value_Stream",
            layer=ArchiMateLayer.STRATEGY,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )