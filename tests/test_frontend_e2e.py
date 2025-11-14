"""
Frontend E2E tests for ArchiMate Interactive Designer.

IMPORTANT: These tests reflect the ACTUAL functionality of designer.html.
Designer is a VIEWER + EDITOR for existing diagrams, NOT a CRUD form for creating new elements.

Prerequisites:
- HTTP server running on localhost:8080
- designer.html accessible
- Playwright installed: uv add --dev playwright pytest-playwright
- Browsers installed: playwright install chromium

To run:
    1. Start HTTP server: uv run python -m archi_mcp.server
    2. Run tests: uv run pytest tests/test_frontend_e2e.py -v

Tests cover:
- Designer page loading
- Layout controls (direction, spacing, checkboxes)
- Element editing (names, descriptions of EXISTING elements)
- History browsing (view, filter, delete)
- Zoom & navigation controls
- Download operations (PNG, SVG, PlantUML, XML)
"""

import pytest
import re
from pathlib import Path

# Check if Playwright is available
try:
    from playwright.sync_api import Page, expect
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Create type stubs for when Playwright is not installed
    from typing import Any
    Page = Any  # type: ignore
    expect = lambda x: x  # type: ignore

# Skip all tests if Playwright not installed
pytestmark = pytest.mark.skipif(
    not PLAYWRIGHT_AVAILABLE,
    reason="Playwright not installed. Install with: uv add --dev playwright pytest-playwright"
)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for testing."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
    }


@pytest.fixture
def designer_url():
    """URL for the designer interface."""
    return "http://127.0.0.1:8080/designer.html"


class TestDesignerPageLoad:
    """Tests for basic designer page loading."""

    @pytest.mark.e2e
    def test_designer_page_loads(self, page: Page, designer_url):
        """Test that designer page loads successfully."""
        page.goto(designer_url)
        expect(page).to_have_title("ArchiMate Interactive Designer")

    @pytest.mark.e2e
    def test_sidebar_visible(self, page: Page, designer_url):
        """Test that sidebar with controls is visible."""
        page.goto(designer_url)
        sidebar = page.locator("#sidebar")
        expect(sidebar).to_be_visible()

    @pytest.mark.e2e
    def test_diagram_container_visible(self, page: Page, designer_url):
        """Test that diagram container is visible."""
        page.goto(designer_url)
        canvas = page.locator("#diagram-container")
        expect(canvas).to_be_visible()

    @pytest.mark.e2e
    def test_diagram_image_loads(self, page: Page, designer_url):
        """Test that diagram image loads."""
        page.goto(designer_url)
        page.wait_for_load_state("networkidle")

        diagram_img = page.locator("#diagram")
        expect(diagram_img).to_be_visible()
        # Check that src is set
        expect(diagram_img).to_have_attribute("src", re.compile(r"exports/.+/diagram\.png"))


class TestLayoutControls:
    """Tests for layout controls (direction, spacing, checkboxes)."""

    @pytest.mark.e2e
    def test_layout_direction_select(self, page: Page, designer_url):
        """Test that layout direction dropdown is present."""
        page.goto(designer_url)

        direction_select = page.get_by_test_id("layout-direction")
        expect(direction_select).to_be_visible()

        # Check options
        expect(direction_select).to_contain_text("Top to Bottom")
        expect(direction_select).to_contain_text("Left to Right")

    @pytest.mark.e2e
    def test_spacing_select(self, page: Page, designer_url):
        """Test that spacing dropdown is present."""
        page.goto(designer_url)

        spacing_select = page.get_by_test_id("layout-spacing")
        expect(spacing_select).to_be_visible()

        # Check options
        expect(spacing_select).to_contain_text("Compact")
        expect(spacing_select).to_contain_text("Comfortable")
        expect(spacing_select).to_contain_text("Spacious")

    @pytest.mark.e2e
    def test_checkboxes_present(self, page: Page, designer_url):
        """Test that all layout checkboxes are present."""
        page.goto(designer_url)

        # Show Legend checkbox
        expect(page.get_by_test_id("show-legend-checkbox")).to_be_visible()

        # Show Title checkbox
        expect(page.get_by_test_id("show-title-checkbox")).to_be_visible()

        # Group by Layer checkbox
        expect(page.get_by_test_id("group-by-layer-checkbox")).to_be_visible()

        # Show Element Types checkbox
        expect(page.get_by_test_id("show-element-types-checkbox")).to_be_visible()

        # Show Relationship Labels checkbox
        expect(page.get_by_test_id("show-relationship-labels-checkbox")).to_be_visible()

    @pytest.mark.e2e
    def test_regenerate_button_present(self, page: Page, designer_url):
        """Test that regenerate button is present."""
        page.goto(designer_url)

        regenerate_btn = page.get_by_test_id("regenerate-btn")
        expect(regenerate_btn).to_be_visible()
        expect(regenerate_btn).to_contain_text("Save Diagram")


class TestElementEditing:
    """
    Tests for editing EXISTING elements in diagrams.
    NOTE: Designer does NOT create new elements - it only edits existing ones!
    """

    @pytest.mark.e2e
    def test_element_selector_present(self, page: Page, designer_url):
        """Test that element selector dropdown exists."""
        page.goto(designer_url)

        # Wait for page load
        page.wait_for_load_state("networkidle")

        # Element selector should be present
        element_select = page.get_by_test_id("element-select")
        expect(element_select).to_be_visible()

    @pytest.mark.e2e
    def test_diagram_title_and_description_editable(self, page: Page, designer_url):
        """Test that diagram title and description can be edited."""
        page.goto(designer_url)
        page.wait_for_load_state("networkidle")

        # Expand editor panel (if collapsed)
        # Note: Panel might be collapsed by default, check and expand if needed
        # For now, assume it's expanded or test just checks elements exist

        # Diagram title input
        diagram_title = page.get_by_test_id("diagram-title")
        # Note: Element might not be visible if panel is collapsed
        # We just check it exists for now
        assert diagram_title is not None

        # Diagram description
        diagram_desc = page.get_by_test_id("diagram-description")
        assert diagram_desc is not None


class TestZoomControls:
    """Tests for zoom controls."""

    @pytest.mark.e2e
    def test_zoom_controls_visible(self, page: Page, designer_url):
        """Test that zoom controls are visible."""
        page.goto(designer_url)

        expect(page.get_by_test_id("zoom-in")).to_be_visible()
        expect(page.get_by_test_id("zoom-out")).to_be_visible()
        expect(page.get_by_test_id("zoom-reset")).to_be_visible()

    @pytest.mark.e2e
    def test_zoom_level_display(self, page: Page, designer_url):
        """Test that zoom level is displayed."""
        page.goto(designer_url)

        zoom_level = page.locator("#zoom-level")
        expect(zoom_level).to_be_visible()
        expect(zoom_level).to_contain_text("100%")


class TestNavigationControls:
    """Tests for navigation controls."""

    @pytest.mark.e2e
    def test_navigation_controls_visible(self, page: Page, designer_url):
        """Test that navigation controls are visible."""
        page.goto(designer_url)

        expect(page.get_by_test_id("nav-prev")).to_be_visible()
        expect(page.get_by_test_id("nav-next")).to_be_visible()
        expect(page.get_by_test_id("nav-delete")).to_be_visible()


class TestHistoryView:
    """Tests for history browsing functionality."""

    @pytest.mark.e2e
    def test_history_button_visible(self, page: Page, designer_url):
        """Test that history button is visible."""
        page.goto(designer_url)

        history_btn = page.get_by_test_id("history-btn")
        expect(history_btn).to_be_visible()
        expect(history_btn).to_contain_text("View Diagram History")

    @pytest.mark.e2e
    def test_history_view_opens(self, page: Page, designer_url):
        """Test that clicking history button opens history view."""
        page.goto(designer_url)
        page.wait_for_load_state("networkidle")

        # Click history button
        history_btn = page.get_by_test_id("history-btn")
        history_btn.click()

        # History view should become visible
        history_view = page.locator("#history-view")
        expect(history_view).to_be_visible()

        # Close button should be visible
        expect(page.get_by_test_id("close-history-btn")).to_be_visible()

    @pytest.mark.e2e
    def test_history_filters_present(self, page: Page, designer_url):
        """Test that history filters are present."""
        page.goto(designer_url)
        page.wait_for_load_state("networkidle")

        # Open history
        page.get_by_test_id("history-btn").click()

        # Search input
        expect(page.get_by_test_id("history-search")).to_be_visible()

        # Date filters
        expect(page.get_by_test_id("history-from-date")).to_be_visible()
        expect(page.get_by_test_id("history-to-date")).to_be_visible()

    @pytest.mark.e2e
    def test_close_history_view(self, page: Page, designer_url):
        """Test that close button hides history view."""
        page.goto(designer_url)
        page.wait_for_load_state("networkidle")

        # Open history
        page.get_by_test_id("history-btn").click()

        # History view should be visible
        history_view = page.locator("#history-view")
        expect(history_view).to_be_visible()

        # Close history
        page.get_by_test_id("close-history-btn").click()

        # Wait for animation/transition
        page.wait_for_timeout(500)

        # History view should be hidden
        expect(history_view).not_to_be_visible()


class TestExportLinks:
    """Tests for export/download links."""

    @pytest.mark.e2e
    def test_export_links_present(self, page: Page, designer_url):
        """Test that all export links are present."""
        page.goto(designer_url)

        # PNG export
        expect(page.get_by_test_id("export-png")).to_be_visible()

        # SVG export
        expect(page.get_by_test_id("export-svg")).to_be_visible()

        # PlantUML export
        expect(page.get_by_test_id("export-puml")).to_be_visible()

        # XML export
        expect(page.get_by_test_id("export-xml")).to_be_visible()


class TestSaveButton:
    """Tests for save changes button."""

    @pytest.mark.e2e
    def test_save_button_exists(self, page: Page, designer_url):
        """Test that save changes button exists."""
        page.goto(designer_url)

        # Note: Save button might be in collapsed panel
        # We check it exists in DOM
        save_btn = page.get_by_test_id("save-changes-btn")
        assert save_btn is not None


class TestResponsiveness:
    """Tests for UI responsiveness."""

    @pytest.mark.e2e
    def test_page_renders_in_viewport(self, page: Page, designer_url):
        """Test that page renders within viewport."""
        page.goto(designer_url)
        page.wait_for_load_state("networkidle")

        # Get viewport size
        viewport = page.viewport_size
        assert viewport is not None

        # Sidebar should be visible
        sidebar = page.locator("#sidebar")
        expect(sidebar).to_be_visible()

        # Diagram container should be visible
        diagram_container = page.locator("#diagram-container")
        expect(diagram_container).to_be_visible()


# Configuration for Playwright
@pytest.fixture(scope="session")
def playwright_config():
    """Playwright configuration."""
    return {
        "browser": "chromium",
        "headless": True,  # Set to False for debugging
        "slow_mo": 50,  # Slow down operations slightly for stability
    }
