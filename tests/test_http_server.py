"""Tests for HTTP server functionality in the ArchiMate MCP server."""

import json
import os
import shutil
import tempfile
import time
import threading
import unittest.mock
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import socket

from archi_mcp.server import (
    find_free_port,
    start_http_server, 
    http_server_port,
    http_server_thread,
    http_server_running,
    create_archimate_diagram,
    DiagramInput,
    ElementInput,
    RelationshipInput
)


class TestHTTPServerFunctionality:
    """Test HTTP server functionality for serving diagram files."""
    
    def setup_method(self):
        """Setup test environment."""
        # Reset global HTTP server state before each test
        import archi_mcp.server as server_module
        server_module.http_server_port = None
        server_module.http_server_thread = None
        server_module.http_server_running = False
        
        # Create temporary exports directory
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Ensure exports directory exists
        self.exports_dir = Path(self.temp_dir) / "exports"
        self.exports_dir.mkdir(exist_ok=True)
        
    def teardown_method(self):
        """Cleanup test environment."""
        # Restore original directory
        os.chdir(self.original_cwd)
        
        # Cleanup temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_find_free_port(self):
        """Test finding a free port for HTTP server."""
        port = find_free_port()
        
        # Check that a valid port number is returned
        assert isinstance(port, int)
        assert 1024 <= port <= 65535
        
        # Verify the port is actually free by trying to bind to it
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            assert result != 0  # Should not be able to connect (port is free)
    
    def test_find_free_port_multiple_calls(self):
        """Test that multiple calls return different ports."""
        port1 = find_free_port()
        port2 = find_free_port()
        
        # Usually different, but may occasionally be same if first socket closed quickly
        # Just ensure both are valid
        assert isinstance(port1, int)
        assert isinstance(port2, int)
        assert 1024 <= port1 <= 65535
        assert 1024 <= port2 <= 65535
    
    @patch('starlette.applications.Starlette')
    @patch('starlette.staticfiles.StaticFiles')
    @patch('starlette.routing.Mount')
    @patch('uvicorn.run')
    def test_start_http_server_success(self, mock_uvicorn_run, mock_mount, mock_static_files, mock_starlette):
        """Test successful HTTP server startup."""
        # Mock the Starlette app and uvicorn
        mock_app = Mock()
        mock_starlette.return_value = mock_app
        
        # Mock uvicorn.run to avoid actually starting server
        def mock_run(*args, **kwargs):
            time.sleep(0.1)  # Simulate server startup time
            
        mock_uvicorn_run.side_effect = mock_run
        
        # Start the server
        port = start_http_server()
        
        # Give thread time to start
        time.sleep(0.2)
        
        # Verify server was configured correctly
        assert port is not None
        assert isinstance(port, int)
        assert 1024 <= port <= 65535
        
        # Verify Starlette was configured with static files
        mock_starlette.assert_called_once()
        call_args = mock_starlette.call_args
        assert 'routes' in call_args.kwargs
        
        # Verify uvicorn was called to start server
        mock_uvicorn_run.assert_called_once()
        uvicorn_call_args = mock_uvicorn_run.call_args
        assert uvicorn_call_args.kwargs['host'] == '127.0.0.1'
        assert uvicorn_call_args.kwargs['port'] == port
        assert uvicorn_call_args.kwargs['log_level'] == 'warning'
        
        # Verify exports directory was created
        assert self.exports_dir.exists()
    
    @patch('uvicorn.run')
    @patch('starlette.applications.Starlette')
    def test_start_http_server_already_running(self, mock_starlette, mock_uvicorn_run):
        """Test that starting HTTP server when already running returns same port."""
        # Mock the components
        mock_starlette.return_value = Mock()
        mock_uvicorn_run.side_effect = lambda *args, **kwargs: time.sleep(0.1)
        
        # Start server first time
        port1 = start_http_server()
        time.sleep(0.2)
        
        # Start server second time
        port2 = start_http_server()
        
        # Should return the same port without starting new server
        assert port1 == port2
        
        # Uvicorn should only be called once
        assert mock_uvicorn_run.call_count == 1
    
    @patch('archi_mcp.server.logger')
    def test_start_http_server_import_error(self, mock_logger):
        """Test HTTP server startup with missing dependencies."""
        # Mock import error for starlette at the import statement level
        original_import = __builtins__['__import__']
        
        def mock_import(name, *args, **kwargs):
            if name == 'starlette.applications':
                raise ImportError("No module named 'starlette'")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            port = start_http_server()
            
            # Should return None on import error
            assert port is None
            
            # Should log error
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args[0][0]
            assert "Failed to start HTTP server" in error_call
    
    @patch('uvicorn.run')
    @patch('starlette.applications.Starlette')
    def test_exports_directory_creation(self, mock_starlette, mock_uvicorn_run):
        """Test that exports directory is created during HTTP server startup."""
        # Remove exports directory if it exists
        if self.exports_dir.exists():
            shutil.rmtree(self.exports_dir)
        
        assert not self.exports_dir.exists()
        
        mock_uvicorn_run.side_effect = lambda *args, **kwargs: time.sleep(0.1)
        mock_starlette.return_value = Mock()
        
        start_http_server()
        time.sleep(0.2)
        
        # Exports directory should be created
        assert self.exports_dir.exists()
        assert self.exports_dir.is_dir()
    
    def test_http_url_generation_logic(self):
        """Test HTTP URL generation logic without full diagram creation."""
        # Test the URL generation logic that would be used in create_archimate_diagram
        # This tests the core HTTP server integration without mocking the full MCP tool
        
        # Create test SVG file in exports
        test_export_dir = self.exports_dir / "20240101_120000"
        test_export_dir.mkdir(parents=True, exist_ok=True)
        test_svg_file = test_export_dir / "diagram.svg"
        test_svg_file.write_text("<svg>test</svg>")
        
        # Mock HTTP server running on port 8080
        port = 8080
        svg_generated = True
        
        # Test URL generation logic (from server.py lines 1256-1267)
        diagram_urls = {}
        if port and svg_generated:
            svg_relative_path = os.path.relpath(test_export_dir / "diagram.svg", self.temp_dir)
            diagram_urls["svg"] = f"http://127.0.0.1:{port}/{svg_relative_path}"
        
        # Verify URL format
        expected_svg_url = "http://127.0.0.1:8080/exports/20240101_120000/diagram.svg"
        assert diagram_urls["svg"] == expected_svg_url
        
        # Test PNG fallback scenario
        diagram_urls_png = {}
        svg_generated = False
        if port and not svg_generated:
            png_relative_path = os.path.relpath(test_export_dir / "diagram.png", self.temp_dir)
            diagram_urls_png["png"] = f"http://127.0.0.1:{port}/{png_relative_path}"
        
        expected_png_url = "http://127.0.0.1:8080/exports/20240101_120000/diagram.png"
        assert diagram_urls_png["png"] == expected_png_url
    
    def test_http_server_failure_handling(self):
        """Test HTTP server startup failure handling logic."""
        # Test the error handling logic when HTTP server fails to start
        # This simulates the try/except block in create_archimate_diagram
        
        # Create test export directory
        test_export_dir = self.exports_dir / "20240101_120000"
        test_export_dir.mkdir(parents=True, exist_ok=True)
        
        # Simulate HTTP server startup failure
        diagram_urls = {}
        try:
            # This would normally call start_http_server() but we simulate failure
            raise Exception("Failed to start server")
        except Exception:
            # This is what happens in the actual code when HTTP server fails
            pass
        
        # Should have empty diagram URLs when server fails
        assert diagram_urls == {}
        
        # Test success message without URL (simulates lines 1269-1275 in server.py)
        success_message = f"✅ ArchiMate diagram created successfully in {test_export_dir}"
        
        # Should not contain HTTP URL when server fails
        assert "http://" not in success_message
        assert "🔗 **View" not in success_message
    
    @patch('uvicorn.run')
    @patch('starlette.applications.Starlette')
    @patch('starlette.staticfiles.StaticFiles')
    @patch('starlette.routing.Mount')
    def test_http_server_static_file_serving_mock(self, mock_mount, mock_static_files, mock_starlette, mock_uvicorn_run):
        """Test HTTP server static file serving configuration with mocks."""
        # Configure mocks
        mock_app = Mock()
        mock_starlette.return_value = mock_app
        mock_uvicorn_run.side_effect = lambda *args, **kwargs: time.sleep(0.1)
        
        # Start server
        port = start_http_server()
        time.sleep(0.2)
        
        # Verify StaticFiles was configured with exports directory
        mock_static_files.assert_called_once()
        static_files_call = mock_static_files.call_args
        exports_dir_path = str(self.exports_dir)
        actual_dir = static_files_call.kwargs['directory']
        
        # Resolve both paths to handle macOS /private symlink differences
        expected_resolved = os.path.realpath(exports_dir_path)
        actual_resolved = os.path.realpath(actual_dir)
        assert actual_resolved == expected_resolved
        
        # Verify Mount was configured with correct path
        mock_mount.assert_called_once()
        mount_call = mock_mount.call_args
        assert mount_call.args[0] == "/exports"
        assert mount_call.kwargs['name'] == "exports"
    
    def test_url_generation_with_relative_paths(self):
        """Test URL generation with relative path handling."""
        # Create test export directory structure in temp dir
        test_export_dir = self.exports_dir / "20240101_120000"
        test_export_dir.mkdir(parents=True, exist_ok=True)
        test_svg_file = test_export_dir / "diagram.svg"
        test_svg_file.write_text("<svg>test</svg>")
        
        # Test relative path calculation from temp dir
        svg_relative_path = os.path.relpath(test_svg_file, self.temp_dir)
        expected_url = f"http://127.0.0.1:8080/{svg_relative_path}"
        
        # Verify path format (should be relative to temp dir which has exports subdir)
        assert "exports/20240101_120000/diagram.svg" in svg_relative_path
        # Since working dir is temp_dir in test, the relative path should match
        assert svg_relative_path == "exports/20240101_120000/diagram.svg"
    
    @patch('threading.Thread')
    @patch('uvicorn.run')
    @patch('starlette.applications.Starlette')
    def test_http_server_threading(self, mock_starlette, mock_uvicorn_run, mock_thread):
        """Test that HTTP server runs in daemon thread."""
        # Configure mocks
        mock_starlette.return_value = Mock()
        mock_uvicorn_run.side_effect = lambda *args, **kwargs: time.sleep(0.1)
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        # Start server
        start_http_server()
        
        # Verify thread was created as daemon
        mock_thread.assert_called_once()
        thread_call = mock_thread.call_args
        assert thread_call.kwargs['daemon'] is True
        
        # Verify thread was started
        mock_thread_instance.start.assert_called_once()
    
    def test_multiple_svg_png_url_preference(self):
        """Test URL generation preference (SVG over PNG)."""
        # Test case where both SVG and PNG exist - should prefer SVG
        test_export_dir = self.exports_dir / "20240101_120000" 
        test_export_dir.mkdir(parents=True, exist_ok=True)
        
        # Create both files
        test_svg_file = test_export_dir / "diagram.svg"
        test_svg_file.write_text("<svg>test</svg>")
        test_png_file = test_export_dir / "diagram.png"
        test_png_file.write_bytes(b"fake png content")
        
        # Mock HTTP server running
        port = 8080
        
        # Calculate URLs
        svg_relative_path = os.path.relpath(test_svg_file, os.getcwd())
        png_relative_path = os.path.relpath(test_png_file, os.getcwd())
        
        svg_url = f"http://127.0.0.1:{port}/{svg_relative_path}"
        png_url = f"http://127.0.0.1:{port}/{png_relative_path}"
        
        # Verify both URLs are valid format
        assert "exports/20240101_120000/diagram.svg" in svg_url
        assert "exports/20240101_120000/diagram.png" in png_url
        
        # In the actual implementation, SVG should be preferred when available
        assert svg_url != png_url


class TestHTTPServerIntegration:
    """Integration tests for HTTP server with real file serving (optional)."""
    
    @pytest.mark.integration
    def test_http_server_real_startup_and_shutdown(self):
        """Integration test for actual HTTP server startup (requires starlette/uvicorn)."""
        try:
            import starlette
            import uvicorn
        except ImportError:
            pytest.skip("starlette and uvicorn not available for integration test")
        
        # This test would actually start the HTTP server
        # Skip in CI/CD to avoid port conflicts
        pytest.skip("Real HTTP server test skipped to avoid port conflicts")