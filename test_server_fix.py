#!/usr/bin/env python3

from archi_mcp.archimate.relationships import ArchiMateRelationship
from archi_mcp.archimate.elements.base import ArchiMateElement, ArchiMateLayer, ArchiMateAspect
from archi_mcp.archimate.generator import ArchiMateGenerator
from enum import Enum

class TestRelType(str, Enum):
    SERVING = "Serving"

# Test the fix directly
print("Testing relationship direction fix...")

# Create a relationship with direction
rel = ArchiMateRelationship(
    id="test_rel",
    from_element="elem1", 
    to_element="elem2",
    relationship_type=TestRelType.SERVING,
    direction="top-bottom",  # This should not break anymore
    label="test relationship"
)

# Generate PlantUML
plantuml = rel.to_plantuml(show_labels=True)
print(f"Generated PlantUML: {plantuml}")

# This should NOT contain "Rel_Serving_top-bottom" but just "Rel_Serving" 
if "_top-bottom" in plantuml:
    print("❌ FAILED: Direction suffix still present!")
else:
    print("✅ SUCCESS: Direction suffix removed!")

# Test with a generator
generator = ArchiMateGenerator()

node = ArchiMateElement(
    id="node1",
    name="Test Node",
    element_type="Node", 
    layer=ArchiMateLayer.TECHNOLOGY,
    aspect=ArchiMateAspect.ACTIVE_STRUCTURE
)

service = ArchiMateElement(
    id="service1", 
    name="Test Service",
    element_type="Technology_Service",
    layer=ArchiMateLayer.TECHNOLOGY, 
    aspect=ArchiMateAspect.BEHAVIOR
)

generator.add_element(node)
generator.add_element(service)
generator.add_relationship(rel)

full_plantuml = generator.generate() 
print("\nFull PlantUML preview:")
print("=" * 50)
print(full_plantuml[:300] + "...")

# Save for testing
with open("/Users/patrik/Projects/archi-mcp/test_server_generated.puml", "w") as f:
    f.write(full_plantuml)

print("✅ Test completed successfully!")