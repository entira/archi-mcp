"""Motivation layer ArchiMate elements."""

from .base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect


class MotivationElement(ArchiMateElement):
    """Base class for Motivation layer elements."""
    
    layer: ArchiMateLayer = ArchiMateLayer.MOTIVATION
    
    @classmethod
    def create_stakeholder(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Stakeholder element."""
        return cls(
            id=id,
            name=name,
            element_type="Stakeholder",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.ACTIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_driver(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Driver element."""
        return cls(
            id=id,
            name=name,
            element_type="Driver",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_assessment(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create an Assessment element."""
        return cls(
            id=id,
            name=name,
            element_type="Assessment",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_goal(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Goal element."""
        return cls(
            id=id,
            name=name,
            element_type="Goal",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_outcome(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create an Outcome element."""
        return cls(
            id=id,
            name=name,
            element_type="Outcome",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_principle(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Principle element."""
        return cls(
            id=id,
            name=name,
            element_type="Principle",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_requirement(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Requirement element."""
        return cls(
            id=id,
            name=name,
            element_type="Requirement",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_constraint(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Constraint element."""
        return cls(
            id=id,
            name=name,
            element_type="Constraint",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.BEHAVIOR,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_meaning(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Meaning element."""
        return cls(
            id=id,
            name=name,
            element_type="Meaning",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )
    
    @classmethod
    def create_value(
        cls,
        id: str,
        name: str,
        description: str = None,
        **kwargs
    ) -> "MotivationElement":
        """Create a Value element."""
        return cls(
            id=id,
            name=name,
            element_type="Value",
            layer=ArchiMateLayer.MOTIVATION,
            aspect=ArchiMateAspect.PASSIVE_STRUCTURE,
            description=description,
            **kwargs
        )