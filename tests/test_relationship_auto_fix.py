"""
Comprehensive tests for ArchiMate Relationship Auto-Fix System.

Tests cover:
- RelationshipAutoFixer class initialization
- fix_xml_relationships() with various scenarios
- get_fix_summary() with different states
- get_suggested_fixes() functionality
- apply_auto_fix() helper function
- All auto-fix rules from AUTO_FIX_RULES
- Edge cases (malformed XML, unknown types, etc.)

Target coverage: 95%+
"""

import pytest
from archi_mcp.xml_export.relationship_auto_fix import (
    RelationshipAutoFixer,
    apply_auto_fix,
    AUTO_FIX_RULES,
    RELATIONSHIP_DESCRIPTIONS,
)


class TestRelationshipAutoFixer:
    """Tests for RelationshipAutoFixer class."""

    def test_init_enabled(self):
        """Test initialization with auto-fix enabled."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        assert fixer.enable_auto_fix is True
        assert fixer.fixes_applied == []

    def test_init_disabled(self):
        """Test initialization with auto-fix disabled."""
        fixer = RelationshipAutoFixer(enable_auto_fix=False)
        assert fixer.enable_auto_fix is False
        assert fixer.fixes_applied == []

    def test_init_default(self):
        """Test default initialization (auto-fix enabled)."""
        fixer = RelationshipAutoFixer()
        assert fixer.enable_auto_fix is True


class TestFixXMLRelationships:
    """Tests for fix_xml_relationships() method."""

    def test_fix_disabled_returns_unchanged(self):
        """Test that disabled fixer returns unchanged content."""
        fixer = RelationshipAutoFixer(enable_auto_fix=False)
        xml = '<model>test</model>'

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert fixed_xml == xml
        assert fixes == []

    def test_fix_no_relationships_to_fix(self):
        """Test XML with no relationships needing fixes."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Business" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="Customer"/>
    <element xsi:type="archimate:BusinessRole" id="elem2" name="Manager"/>
    <element xsi:type="archimate:AssignmentRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # No fixes should be applied
        assert fixed_xml == xml
        assert fixes == []

    def test_fix_cross_layer_access_issue(self):
        """Test fixing cross-layer AccessRelationship issue."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Business" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="Customer"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="Web Portal"/>
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # Should replace AccessRelationship with AssociationRelationship
        assert 'xsi:type="archimate:AssociationRelationship"' in fixed_xml
        assert 'xsi:type="archimate:AccessRelationship"' not in fixed_xml
        assert len(fixes) == 1
        assert "BusinessActor" in fixes[0]
        assert "AssociationRelationship" in fixes[0]

    def test_fix_business_to_application_assignment(self):
        """Test fixing BusinessActor -> ApplicationService AssignmentRelationship."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Mixed" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationService" id="elem2" name="API"/>
    <element xsi:type="archimate:AssignmentRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # Should replace AssignmentRelationship with ServingRelationship
        assert 'xsi:type="archimate:ServingRelationship"' in fixed_xml
        assert len(fixes) == 1
        assert "ServingRelationship" in fixes[0]

    def test_fix_multiple_relationships(self):
        """Test fixing multiple relationships in one pass."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Mixed" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
    <element xsi:type="archimate:ApplicationService" id="elem3" name="Service"/>

    <element xsi:type="archimate:AccessRelationship" id="rel1" source="elem1" target="elem2"/>
    <element xsi:type="archimate:AssignmentRelationship" id="rel2" source="elem1" target="elem3"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # Should fix both relationships
        assert len(fixes) == 2
        assert 'xsi:type="archimate:AssociationRelationship"' in fixed_xml
        assert 'xsi:type="archimate:ServingRelationship"' in fixed_xml

    def test_fix_with_unknown_element_type(self):
        """Test handling of relationships with unknown element types."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="missing1" target="missing2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # Should not fix relationships with unknown types
        assert fixed_xml == xml
        assert fixes == []

    def test_fix_with_attributes_preserved(self):
        """Test that relationship attributes are preserved during fix."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="elem1" target="elem2" name="uses" documentation="test doc"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # Attributes should be preserved
        assert 'name="uses"' in fixed_xml
        assert 'documentation="test doc"' in fixed_xml
        assert 'xsi:type="archimate:AssociationRelationship"' in fixed_xml


class TestGetFixSummary:
    """Tests for get_fix_summary() method."""

    def test_summary_no_fixes(self):
        """Test summary when no fixes applied."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)

        summary = fixer.get_fix_summary()

        assert "No relationship fixes needed" in summary
        assert "✅" in summary

    def test_summary_with_fixes(self):
        """Test summary with fixes applied."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        # Simulate fixes being applied
        fixer.fixes_applied = [
            "Fixed rel1: BusinessActor --[AccessRelationship]--> ApplicationComponent → AssociationRelationship",
            "Fixed rel2: BusinessActor --[AssignmentRelationship]--> ApplicationService → ServingRelationship"
        ]

        summary = fixer.get_fix_summary()

        assert "Applied 2 relationship fixes" in summary
        assert "rel1" in summary
        assert "rel2" in summary
        assert "🔧" in summary

    def test_summary_single_fix(self):
        """Test summary with single fix."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        fixer.fixes_applied = ["Fixed rel1: Test fix"]

        summary = fixer.get_fix_summary()

        assert "Applied 1 relationship fix" in summary
        assert "Test fix" in summary


class TestGetSuggestedFixes:
    """Tests for get_suggested_fixes() method."""

    def test_suggestions_for_fixable_relationships(self):
        """Test getting suggestions for fixable relationships."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        suggestions = fixer.get_suggested_fixes(xml)

        assert len(suggestions) == 1
        assert "rel1" in suggestions[0]
        assert "Suggest: AssociationRelationship" in suggestions[0]
        assert "Association (general relationship)" in suggestions[0]

    def test_suggestions_empty_for_valid_relationships(self):
        """Test no suggestions for already valid relationships."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:BusinessRole" id="elem2" name="Manager"/>
    <element xsi:type="archimate:AssignmentRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        suggestions = fixer.get_suggested_fixes(xml)

        assert suggestions == []

    def test_suggestions_skip_unknown_types(self):
        """Test suggestions skip relationships with unknown types."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="unknown1" target="unknown2"/>
  </folder>
</archimate:model>'''

        suggestions = fixer.get_suggested_fixes(xml)

        assert suggestions == []


class TestApplyAutoFix:
    """Tests for apply_auto_fix() helper function."""

    def test_apply_auto_fix_enabled(self):
        """Test apply_auto_fix with fix enabled."""
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fix_info = apply_auto_fix(xml, enable_fix=True)

        assert 'xsi:type="archimate:AssociationRelationship"' in fixed_xml
        assert fix_info["fix_count"] == 1
        assert len(fix_info["fixes_applied"]) == 1
        assert fix_info["suggestions"] == []
        assert "Applied 1 relationship fix" in fix_info["summary"]

    def test_apply_auto_fix_disabled(self):
        """Test apply_auto_fix with fix disabled (suggestions only)."""
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
    <element xsi:type="archimate:AccessRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fix_info = apply_auto_fix(xml, enable_fix=False)

        # Content unchanged
        assert fixed_xml == xml
        assert fix_info["fix_count"] == 0
        assert fix_info["fixes_applied"] == []
        assert fix_info["suggestion_count"] == 1
        assert len(fix_info["suggestions"]) == 1
        assert "Found 1 fixable relationship" in fix_info["summary"]

    def test_apply_auto_fix_no_issues(self):
        """Test apply_auto_fix with valid XML (no issues)."""
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:BusinessRole" id="elem2" name="Manager"/>
    <element xsi:type="archimate:AssignmentRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fix_info = apply_auto_fix(xml, enable_fix=True)

        assert fixed_xml == xml
        assert fix_info["fix_count"] == 0
        assert fix_info["suggestion_count"] == 0


class TestAutoFixRules:
    """Tests for specific auto-fix rules."""

    def test_rule_business_process_to_application_realization(self):
        """Test BusinessProcess -> ApplicationComponent RealizationRelationship fix."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessProcess" id="elem1" name="Process"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
    <element xsi:type="archimate:RealizationRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert 'xsi:type="archimate:TriggeringRelationship"' in fixed_xml
        assert len(fixes) == 1

    def test_rule_motivation_to_implementation(self):
        """Test Motivation -> Implementation layer fix."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:Principle" id="elem1" name="Principle1"/>
    <element xsi:type="archimate:Deliverable" id="elem2" name="Deliverable1"/>
    <element xsi:type="archimate:InfluenceRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert 'xsi:type="archimate:AssociationRelationship"' in fixed_xml
        assert len(fixes) == 1

    def test_rule_business_role_location(self):
        """Test BusinessRole -> Location AssignmentRelationship fix."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessRole" id="elem1" name="Role"/>
    <element xsi:type="archimate:Location" id="elem2" name="Office"/>
    <element xsi:type="archimate:AssignmentRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert 'xsi:type="archimate:AssociationRelationship"' in fixed_xml
        assert len(fixes) == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_xml(self):
        """Test handling of empty XML."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = ""

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert fixed_xml == xml
        assert fixes == []

    def test_malformed_xml(self):
        """Test handling of malformed XML (missing closing tags)."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = "<model><element"

        # Should not crash, just return unchanged
        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert fixed_xml == xml
        assert fixes == []

    def test_xml_without_relationships(self):
        """Test XML with only elements, no relationships."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:ApplicationComponent" id="elem2" name="App"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        assert fixed_xml == xml
        assert fixes == []

    def test_relationship_not_in_auto_fix_rules(self):
        """Test relationship combination not in AUTO_FIX_RULES."""
        fixer = RelationshipAutoFixer(enable_auto_fix=True)
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <folder name="Test" id="folder1">
    <element xsi:type="archimate:BusinessActor" id="elem1" name="User"/>
    <element xsi:type="archimate:BusinessRole" id="elem2" name="Manager"/>
    <element xsi:type="archimate:CompositionRelationship" id="rel1" source="elem1" target="elem2"/>
  </folder>
</archimate:model>'''

        fixed_xml, fixes = fixer.fix_xml_relationships(xml)

        # Should not fix (not in rules)
        assert fixed_xml == xml
        assert fixes == []


class TestConstants:
    """Tests for module constants."""

    def test_auto_fix_rules_exist(self):
        """Test that AUTO_FIX_RULES is defined and not empty."""
        assert AUTO_FIX_RULES is not None
        assert len(AUTO_FIX_RULES) > 0
        assert isinstance(AUTO_FIX_RULES, dict)

    def test_relationship_descriptions_exist(self):
        """Test that RELATIONSHIP_DESCRIPTIONS is defined."""
        assert RELATIONSHIP_DESCRIPTIONS is not None
        assert len(RELATIONSHIP_DESCRIPTIONS) > 0
        assert isinstance(RELATIONSHIP_DESCRIPTIONS, dict)

    def test_auto_fix_rules_format(self):
        """Test that AUTO_FIX_RULES entries have correct format."""
        for key, value in AUTO_FIX_RULES.items():
            # Key should be tuple of (source_type, target_type, rel_type)
            assert isinstance(key, tuple)
            assert len(key) == 3
            # Value should be string (new relationship type)
            assert isinstance(value, str)
            assert value.endswith("Relationship")

    def test_relationship_descriptions_coverage(self):
        """Test that common relationship types have descriptions."""
        expected_types = [
            "AssociationRelationship",
            "ServingRelationship",
            "TriggeringRelationship",
            "AccessRelationship",
            "RealizationRelationship",
            "InfluenceRelationship",
            "AssignmentRelationship",
        ]

        for rel_type in expected_types:
            assert rel_type in RELATIONSHIP_DESCRIPTIONS
            assert isinstance(RELATIONSHIP_DESCRIPTIONS[rel_type], str)
            assert len(RELATIONSHIP_DESCRIPTIONS[rel_type]) > 0
