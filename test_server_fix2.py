#!/usr/bin/env python3

from archi_mcp.archimate.relationships import ArchiMateRelationship, RelationshipType, RelationshipDirection
from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.archimate.generator import ArchiMateGenerator

# Test the fix directly
print("Testing relationship direction fix...")

# Test 1: Relationship with valid direction enum
rel1 = ArchiMateRelationship(
    id="test_rel1",
    from_element="elem1", 
    to_element="elem2",
    relationship_type=RelationshipType.SERVING,
    direction=RelationshipDirection.DOWN,  # Valid enum value
    label="test relationship"
)

plantuml1 = rel1.to_plantuml(show_labels=True)
print(f"With direction: {plantuml1}")

# Test 2: Relationship without direction
rel2 = ArchiMateRelationship(
    id="test_rel2",
    from_element="elem1", 
    to_element="elem2", 
    relationship_type=RelationshipType.SERVING,
    label="test relationship without direction"
)

plantuml2 = rel2.to_plantuml(show_labels=True)
print(f"Without direction: {plantuml2}")

# Both should generate "Rel_Serving" not "Rel_Serving_Down"
if "_Down" in plantuml1:
    print("❌ FAILED: Direction suffix still present!")
else:
    print("✅ SUCCESS: Direction suffix removed!")

print("✅ Relationship fix test completed!")