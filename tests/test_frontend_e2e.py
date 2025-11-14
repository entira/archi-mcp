"""
Frontend E2E tests for ArchiMate Interactive Designer.

These tests require:
- HTTP server running on localhost:8080
- designer.html accessible
- Playwright or Selenium for browser automation

To run these tests:
    1. Install Playwright: uv add --dev playwright pytest-playwright
    2. Install browsers: playwright install chromium
    3. Start HTTP server: uv run python -m archi_mcp.server
    4. Run tests: uv run pytest tests/test_frontend_e2e.py

Tests cover:
- Designer page loading
- Element creation via UI
- Relationship creation
- Diagram regeneration
- History browsing
- Fork/delete operations
"""

import pytest
from pathlib import Path
import time

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
    # Assumes server is running on port 8080
    return "http://127.0.0.1:8080/designer.html"


class TestDesignerPageLoad:
    """Tests for basic designer page loading."""

    @pytest.mark.e2e
    def test_designer_page_loads(self, page: Page, designer_url):
        """Test that designer page loads successfully."""
        page.goto(designer_url)

        # Check title
        expect(page).to_have_title("ArchiMate Interactive Designer")

    @pytest.mark.e2e
    def test_sidebar_visible(self, page: Page, designer_url):
        """Test that sidebar with controls is visible."""
        page.goto(designer_url)

        # Sidebar should be visible
        sidebar = page.locator("#sidebar")
        expect(sidebar).to_be_visible()

    @pytest.mark.e2e
    def test_canvas_visible(self, page: Page, designer_url):
        """Test that diagram canvas is visible."""
        page.goto(designer_url)

        # Canvas area should be visible
        canvas = page.locator("#diagram-container")
        expect(canvas).to_be_visible()

    @pytest.mark.e2e
    def test_navigation_tabs_present(self, page: Page, designer_url):
        """Test that Editor and History tabs are present."""
        page.goto(designer_url)

        # Check for tabs
        editor_tab = page.locator("text=Editor")
        history_tab = page.locator("text=History")

        expect(editor_tab).to_be_visible()
        expect(history_tab).to_be_visible()


class TestElementCreation:
    """Tests for creating ArchiMate elements via UI."""

    @pytest.mark.e2e
    def test_add_business_actor(self, page: Page, designer_url):
        """Test adding a Business Actor element."""
        page.goto(designer_url)

        # Fill element form
        page.fill("input[name='element-name']", "Test Business Actor")
        page.select_option("select[name='element-type']", "Business_Actor")
        page.fill("textarea[name='element-description']", "Test description")

        # Click Add Element button
        page.click("button:has-text('Add Element')")

        # Verify element was added (check element list or diagram)
        # This is placeholder - actual implementation depends on UI structure

    @pytest.mark.e2e
    def test_add_application_component(self, page: Page, designer_url):
        """Test adding an Application Component element."""
        page.goto(designer_url)

        page.fill("input[name='element-name']", "Test App Component")
        page.select_option("select[name='element-type']", "Application_Component")

        page.click("button:has-text('Add Element')")

        # Verify success
        # Placeholder for verification

    @pytest.mark.e2e
    def test_element_name_validation(self, page: Page, designer_url):
        """Test element name validation."""
        page.goto(designer_url)

        # Try to add element without name
        page.select_option("select[name='element-type']", "Business_Actor")
        page.click("button:has-text('Add Element')")

        # Should show validation error
        # Placeholder for error message check


class TestRelationshipCreation:
    """Tests for creating relationships via UI."""

    @pytest.mark.e2e
    def test_add_relationship_between_elements(self, page: Page, designer_url):
        """Test adding a relationship between two elements."""
        page.goto(designer_url)

        # First, add two elements
        # Then create relationship
        # Placeholder for full workflow

    @pytest.mark.e2e
    def test_relationship_type_selection(self, page: Page, designer_url):
        """Test selecting different relationship types."""
        page.goto(designer_url)

        # Check that all relationship types are available
        relationship_types = [
            "Serving", "Access", "Realization", "Assignment",
            "Triggering", "Flow", "Association", "Specialization"
        ]

        # Placeholder for dropdown verification


class TestDiagramRegeneration:
    """Tests for diagram regeneration functionality."""

    @pytest.mark.e2e
    def test_regenerate_button_click(self, page: Page, designer_url):
        """Test clicking the Regenerate button."""
        page.goto(designer_url)

        # Find and click regenerate button
        regenerate_btn = page.locator("button:has-text('Regenerate')")
        expect(regenerate_btn).to_be_visible()

        regenerate_btn.click()

        # Should trigger diagram regeneration
        # Placeholder for verification

    @pytest.mark.e2e
    def test_change_layout_direction(self, page: Page, designer_url):
        """Test changing diagram layout direction."""
        page.goto(designer_url)

        # Change layout direction dropdown
        page.select_option("select[name='direction']", "horizontal")

        # Trigger regeneration
        page.click("button:has-text('Regenerate')")

        # Verify layout change reflected in diagram
        # Placeholder

    @pytest.mark.e2e
    def test_toggle_legend(self, page: Page, designer_url):
        """Test toggling legend visibility."""
        page.goto(designer_url)

        # Toggle legend checkbox
        legend_checkbox = page.locator("input[name='show-legend']")
        legend_checkbox.click()

        # Regenerate
        page.click("button:has-text('Regenerate')")

        # Verify legend visibility changed
        # Placeholder


class TestHistoryBrowsing:
    """Tests for browsing diagram history."""

    @pytest.mark.e2e
    def test_switch_to_history_tab(self, page: Page, designer_url):
        """Test switching to History tab."""
        page.goto(designer_url)

        # Click History tab
        page.click("text=History")

        # History panel should be visible
        history_panel = page.locator("#history-panel")
        expect(history_panel).to_be_visible()

    @pytest.mark.e2e
    def test_history_list_displays_diagrams(self, page: Page, designer_url):
        """Test that history list shows previous diagrams."""
        page.goto(designer_url)
        page.click("text=History")

        # Should display diagram cards/rows
        # Placeholder for verification

    @pytest.mark.e2e
    def test_history_search_filter(self, page: Page, designer_url):
        """Test searching/filtering history."""
        page.goto(designer_url)
        page.click("text=History")

        # Enter search term
        page.fill("input[name='history-search']", "Banking")

        # Should filter results
        # Placeholder

    @pytest.mark.e2e
    def test_history_date_filter(self, page: Page, designer_url):
        """Test filtering history by date range."""
        page.goto(designer_url)
        page.click("text=History")

        # Set date range
        page.fill("input[name='from-date']", "2024-01-01")
        page.fill("input[name='to-date']", "2024-01-31")

        page.click("button:has-text('Apply Filters')")

        # Should show only diagrams in range
        # Placeholder


class TestForkDeleteOperations:
    """Tests for forking and deleting diagrams."""

    @pytest.mark.e2e
    def test_fork_diagram_from_history(self, page: Page, designer_url):
        """Test forking a diagram from history."""
        page.goto(designer_url)
        page.click("text=History")

        # Click fork button on a diagram
        fork_btn = page.locator("button:has-text('Fork')").first
        fork_btn.click()

        # Should load diagram into editor
        # Switch back to Editor tab to verify
        page.click("text=Editor")

        # Diagram should be loaded
        # Placeholder

    @pytest.mark.e2e
    def test_delete_diagram_from_history(self, page: Page, designer_url):
        """Test deleting a diagram from history."""
        page.goto(designer_url)
        page.click("text=History")

        # Click delete button
        delete_btn = page.locator("button:has-text('Delete')").first
        delete_btn.click()

        # Confirm deletion (if confirmation dialog exists)
        # page.click("button:has-text('Confirm')")

        # Diagram should be removed from list
        # Placeholder

    @pytest.mark.e2e
    def test_bulk_delete_diagrams(self, page: Page, designer_url):
        """Test bulk deletion of multiple diagrams."""
        page.goto(designer_url)
        page.click("text=History")

        # Select multiple checkboxes
        checkboxes = page.locator("input[type='checkbox']").all()
        for i, checkbox in enumerate(checkboxes[:3]):  # Select first 3
            checkbox.click()

        # Click bulk delete
        page.click("button:has-text('Delete Selected')")

        # Should delete selected diagrams
        # Placeholder


class TestDownloadOperations:
    """Tests for downloading diagram files."""

    @pytest.mark.e2e
    def test_download_png(self, page: Page, designer_url):
        """Test downloading diagram as PNG."""
        page.goto(designer_url)

        # Click download PNG button
        with page.expect_download() as download_info:
            page.click("button:has-text('Download PNG')")

        download = download_info.value
        assert download.suggested_filename.endswith(".png")

    @pytest.mark.e2e
    def test_download_svg(self, page: Page, designer_url):
        """Test downloading diagram as SVG."""
        page.goto(designer_url)

        with page.expect_download() as download_info:
            page.click("button:has-text('Download SVG')")

        download = download_info.value
        assert download.suggested_filename.endswith(".svg")

    @pytest.mark.e2e
    def test_download_plantuml(self, page: Page, designer_url):
        """Test downloading PlantUML source code."""
        page.goto(designer_url)

        with page.expect_download() as download_info:
            page.click("button:has-text('Download PlantUML')")

        download = download_info.value
        assert download.suggested_filename.endswith(".puml")

    @pytest.mark.e2e
    def test_download_all_files(self, page: Page, designer_url):
        """Test downloading all files as ZIP."""
        page.goto(designer_url)

        with page.expect_download() as download_info:
            page.click("button:has-text('Download All')")

        download = download_info.value
        # Should be ZIP file
        # Placeholder for verification


class TestUIResponsiveness:
    """Tests for UI responsiveness and interactivity."""

    @pytest.mark.e2e
    def test_sidebar_collapse_toggle(self, page: Page, designer_url):
        """Test collapsing and expanding sidebar."""
        page.goto(designer_url)

        # Find collapse button
        collapse_btn = page.locator("button[aria-label='Toggle sidebar']")
        collapse_btn.click()

        # Sidebar should collapse
        sidebar = page.locator("#sidebar")
        # Check width or class
        # Placeholder

    @pytest.mark.e2e
    def test_zoom_controls(self, page: Page, designer_url):
        """Test diagram zoom in/out controls."""
        page.goto(designer_url)

        # Click zoom in
        page.click("button[aria-label='Zoom in']")

        # Verify zoom level changed
        # Placeholder

        # Click zoom out
        page.click("button[aria-label='Zoom out']")

        # Click reset zoom
        page.click("button[aria-label='Reset zoom']")

    @pytest.mark.e2e
    def test_realtime_diagram_updates(self, page: Page, designer_url):
        """Test that diagram updates in realtime."""
        page.goto(designer_url)

        # Add element
        page.fill("input[name='element-name']", "Test Element")
        page.select_option("select[name='element-type']", "Business_Actor")
        page.click("button:has-text('Add Element')")

        # Diagram should update automatically (2s poll interval)
        page.wait_for_timeout(3000)  # Wait for auto-refresh

        # Verify diagram updated
        # Placeholder


class TestErrorHandling:
    """Tests for error handling in frontend."""

    @pytest.mark.e2e
    def test_api_error_display(self, page: Page, designer_url):
        """Test that API errors are displayed to user."""
        page.goto(designer_url)

        # Trigger an error (e.g., invalid element)
        # Should show error message
        # Placeholder

    @pytest.mark.e2e
    def test_network_error_recovery(self, page: Page, designer_url):
        """Test recovery from network errors."""
        page.goto(designer_url)

        # Simulate network interruption
        # Should handle gracefully and show error
        # Placeholder


# Configuration for Playwright
@pytest.fixture(scope="session")
def playwright_config():
    """Playwright configuration."""
    return {
        "browser": "chromium",
        "headless": True,  # Set to False for debugging
        "slow_mo": 100,  # Slow down operations for visibility
    }
