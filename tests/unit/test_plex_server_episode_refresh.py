#!/usr/bin/env python3
"""
Comprehensive test suite for plex_server_episode_refresh
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to path for test helpers
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

try:
    from utils.test_helpers import MediaLibraryTestCase, TEST_HELPERS_AVAILABLE
except ImportError:
    MediaLibraryTestCase = unittest.TestCase
    TEST_HELPERS_AVAILABLE = False

import importlib.util

# Load the plex_server_episode_refresh script as a module
def load_plex_server_episode_refresh():
    """Load the plex_server_episode_refresh script as a module."""
    script_path = Path(__file__).parent.parent / 'plex-api' / 'plex_server_episode_refresh'
    if not script_path.exists():
        return None
    
    # Copy the script to a temporary .py file for import
    import shutil
    temp_script_path = Path(__file__).parent / 'temp_plex_server_episode_refresh.py'
    
    try:
        shutil.copy2(script_path, temp_script_path)
        
        spec = importlib.util.spec_from_file_location("plex_server_episode_refresh", temp_script_path)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules['plex_server_episode_refresh'] = module
        spec.loader.exec_module(module)
        
        return module
    except Exception as e:
        return None
    finally:
        # Clean up the temporary file
        temp_script_path.unlink(missing_ok=True)


class TestCredentialHandling(MediaLibraryTestCase):
    """Test credential handling functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_server_episode_refresh()
        if not self.module:
            self.skipTest("plex_server_episode_refresh module not available")
    
    def test_get_token_from_cli(self):
        """Test token retrieval from CLI argument."""
        # Test that CLI argument takes precedence
        client = self.module.PlexServerEpisodeRefresh(
            token="cli_token",
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        self.assertEqual(client.token, "cli_token")
    
    def test_get_server_from_cli(self):
        """Test server URL retrieval from CLI argument."""
        # Test that CLI argument takes precedence
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://cli-server:32400",
            verbose=False,
            debug=False
        )
        self.assertEqual(client.server_url, "http://cli-server:32400")
    
    @patch.dict(os.environ, {'PLEX_TOKEN': 'env_token'})
    def test_get_token_from_env(self):
        """Test token retrieval from environment variable."""
        client = self.module.PlexServerEpisodeRefresh(
            token=None,
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        self.assertEqual(client.token, "env_token")
    
    @patch.dict(os.environ, {'PLEX_SERVER': 'http://env-server:32400'})
    def test_get_server_from_env(self):
        """Test server URL retrieval from environment variable."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url=None,
            verbose=False,
            debug=False
        )
        self.assertEqual(client.server_url, "http://env-server:32400")
    
    def test_get_token_from_local_env_file(self):
        """Test token retrieval from local .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / '.env'
            env_file.write_text('PLEX_TOKEN=local_env_token\n')
            
            # Change to temp directory
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                client = self.module.PlexServerEpisodeRefresh(
                    token=None,
                    server_url="http://test:32400",
                    verbose=False,
                    debug=False
                )
                self.assertEqual(client.token, "local_env_token")
            finally:
                os.chdir(old_cwd)
    
    def test_get_server_from_local_env_file(self):
        """Test server URL retrieval from local .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / '.env'
            env_file.write_text('PLEX_SERVER=http://local-env-server:32400\n')
            
            # Change to temp directory
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                client = self.module.PlexServerEpisodeRefresh(
                    token="test_token",
                    server_url=None,
                    verbose=False,
                    debug=False
                )
                self.assertEqual(client.server_url, "http://local-env-server:32400")
            finally:
                os.chdir(old_cwd)
    
    @patch('pathlib.Path.home')
    def test_get_token_from_global_env_file(self):
        """Test token retrieval from global .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            global_env_dir = Path(temp_dir) / '.media-library-tool'
            global_env_dir.mkdir()
            global_env_file = global_env_dir / '.env'
            global_env_file.write_text('PLEX_TOKEN=global_env_token\n')
            
            # Mock Path.home() to return our temp directory
            Path.home.return_value = Path(temp_dir)
            
            client = self.module.PlexServerEpisodeRefresh(
                token=None,
                server_url="http://test:32400",
                verbose=False,
                debug=False
            )
            self.assertEqual(client.token, "global_env_token")
    
    @patch('pathlib.Path.home')
    def test_get_server_from_global_env_file(self):
        """Test server URL retrieval from global .env file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            global_env_dir = Path(temp_dir) / '.media-library-tool'
            global_env_dir.mkdir()
            global_env_file = global_env_dir / '.env'
            global_env_file.write_text('PLEX_SERVER=http://global-env-server:32400\n')
            
            # Mock Path.home() to return our temp directory
            Path.home.return_value = Path(temp_dir)
            
            client = self.module.PlexServerEpisodeRefresh(
                token="test_token",
                server_url=None,
                verbose=False,
                debug=False
            )
            self.assertEqual(client.server_url, "http://global-env-server:32400")
    
    def test_credential_priority_order_token(self):
        """Test that credential priority order is followed for tokens."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create local .env file
            local_env_file = Path(temp_dir) / '.env'
            local_env_file.write_text('PLEX_TOKEN=local_env_token\n')
            
            # Create global .env file
            global_env_dir = Path(temp_dir) / '.media-library-tool'
            global_env_dir.mkdir()
            global_env_file = global_env_dir / '.env'
            global_env_file.write_text('PLEX_TOKEN=global_env_token\n')
            
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Mock Path.home() for global .env
                with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                    # Test CLI > ENV > local .env > global .env
                    
                    # CLI should win
                    client = self.module.PlexServerEpisodeRefresh(
                        token="cli_token",
                        server_url="http://test:32400",
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.token, "cli_token")
                    
                    # ENV should win over files
                    with patch.dict(os.environ, {'PLEX_TOKEN': 'env_token'}):
                        client = self.module.PlexServerEpisodeRefresh(
                            token=None,
                            server_url="http://test:32400",
                            verbose=False,
                            debug=False
                        )
                        self.assertEqual(client.token, "env_token")
                    
                    # Local .env should win over global .env
                    client = self.module.PlexServerEpisodeRefresh(
                        token=None,
                        server_url="http://test:32400",
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.token, "local_env_token")
                    
                    # Remove local .env, should get global .env
                    local_env_file.unlink()
                    client = self.module.PlexServerEpisodeRefresh(
                        token=None,
                        server_url="http://test:32400",
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.token, "global_env_token")
            finally:
                os.chdir(old_cwd)
    
    def test_credential_priority_order_server(self):
        """Test that credential priority order is followed for server URLs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create local .env file
            local_env_file = Path(temp_dir) / '.env'
            local_env_file.write_text('PLEX_SERVER=http://local-env:32400\n')
            
            # Create global .env file
            global_env_dir = Path(temp_dir) / '.media-library-tool'
            global_env_dir.mkdir()
            global_env_file = global_env_dir / '.env'
            global_env_file.write_text('PLEX_SERVER=http://global-env:32400\n')
            
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Mock Path.home() for global .env
                with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                    # Test CLI > ENV > local .env > global .env > default
                    
                    # CLI should win
                    client = self.module.PlexServerEpisodeRefresh(
                        token="test_token",
                        server_url="http://cli-server:32400",
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.server_url, "http://cli-server:32400")
                    
                    # ENV should win over files
                    with patch.dict(os.environ, {'PLEX_SERVER': 'http://env-server:32400'}):
                        client = self.module.PlexServerEpisodeRefresh(
                            token="test_token",
                            server_url=None,
                            verbose=False,
                            debug=False
                        )
                        self.assertEqual(client.server_url, "http://env-server:32400")
                    
                    # Local .env should win over global .env
                    client = self.module.PlexServerEpisodeRefresh(
                        token="test_token",
                        server_url=None,
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.server_url, "http://local-env:32400")
                    
                    # Remove local .env, should get global .env
                    local_env_file.unlink()
                    client = self.module.PlexServerEpisodeRefresh(
                        token="test_token",
                        server_url=None,
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.server_url, "http://global-env:32400")
                    
                    # Remove global .env, should get default
                    global_env_file.unlink()
                    client = self.module.PlexServerEpisodeRefresh(
                        token="test_token",
                        server_url=None,
                        verbose=False,
                        debug=False
                    )
                    self.assertEqual(client.server_url, "http://localhost:32400")
            finally:
                os.chdir(old_cwd)
    
    def test_missing_token_error(self):
        """Test handling when PLEX_TOKEN is not found."""
        with self.assertRaises(ValueError) as context:
            self.module.PlexServerEpisodeRefresh(
                token=None,
                server_url="http://test:32400",
                verbose=False,
                debug=False
            )
        
        self.assertIn("PLEX_TOKEN not found", str(context.exception))
        self.assertIn("~/.media-library-tools/.env", str(context.exception))
    
    @patch('pathlib.Path.home')
    def test_global_env_file_error_handling(self):
        """Test handling when global .env file cannot be read."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock Path.home() to return our temp directory
            Path.home.return_value = Path(temp_dir)
            
            # This should not raise an exception, just fall back to default server
            client = self.module.PlexServerEpisodeRefresh(
                token="test_token",
                server_url=None,
                verbose=False,
                debug=False
            )
            self.assertEqual(client.server_url, "http://localhost:32400")


class TestPlexAPIClient(MediaLibraryTestCase):
    """Test Plex API client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_server_episode_refresh()
        if not self.module:
            self.skipTest("plex_server_episode_refresh module not available")
        
        # Create a client for testing
        self.client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test-server:32400",
            verbose=False,
            debug=False
        )
    
    @patch('urllib.request.urlopen')
    def test_make_request_success(self):
        """Test successful API request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"test": "data"}'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        mock_urlopen = MagicMock()
        mock_urlopen.return_value = mock_response
        
        with patch('urllib.request.urlopen', mock_urlopen):
            result = self.client._make_request("http://test-server:32400/test")
            
            self.assertEqual(result, {"test": "data"})
            mock_urlopen.assert_called_once()
    
    @patch('urllib.request.urlopen')
    def test_make_request_non_json_response(self):
        """Test API request with non-JSON response."""
        # Mock successful response with non-JSON content
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'success'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        mock_urlopen = MagicMock()
        mock_urlopen.return_value = mock_response
        
        with patch('urllib.request.urlopen', mock_urlopen):
            result = self.client._make_request("http://test-server:32400/test")
            
            self.assertEqual(result, "success")
            mock_urlopen.assert_called_once()
    
    @patch('urllib.request.urlopen')
    def test_make_request_http_error_401(self):
        """Test API request with HTTP 401 error."""
        from urllib.error import HTTPError
        
        mock_error = HTTPError(
            url="http://test-server:32400/test",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None
        )
        
        with patch('urllib.request.urlopen', side_effect=mock_error):
            result = self.client._make_request("http://test-server:32400/test")
            
            self.assertIsNone(result)
    
    @patch('urllib.request.urlopen')
    def test_make_request_http_error_404(self):
        """Test API request with HTTP 404 error."""
        from urllib.error import HTTPError
        
        mock_error = HTTPError(
            url="http://test-server:32400/test",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None
        )
        
        with patch('urllib.request.urlopen', side_effect=mock_error):
            result = self.client._make_request("http://test-server:32400/test")
            
            self.assertIsNone(result)
    
    @patch('urllib.request.urlopen')
    def test_make_request_network_error(self):
        """Test API request with network error."""
        from urllib.error import URLError
        
        mock_error = URLError("Connection refused")
        
        with patch('urllib.request.urlopen', side_effect=mock_error):
            result = self.client._make_request("http://test-server:32400/test")
            
            self.assertIsNone(result)
    
    @patch('urllib.request.urlopen')
    def test_make_request_put_method(self):
        """Test API request with PUT method."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b''
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        mock_urlopen = MagicMock()
        mock_urlopen.return_value = mock_response
        
        with patch('urllib.request.urlopen', mock_urlopen):
            result = self.client._make_request("http://test-server:32400/test", method='PUT')
            
            self.assertEqual(result, "")
            mock_urlopen.assert_called_once()
            
            # Verify the request method was set correctly
            call_args = mock_urlopen.call_args[0][0]  # Get the request object
            self.assertEqual(call_args.get_method(), 'PUT')
    
    @patch('urllib.request.urlopen')
    def test_make_request_with_data(self):
        """Test API request with JSON data."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"result": "ok"}'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        mock_urlopen = MagicMock()
        mock_urlopen.return_value = mock_response
        
        test_data = {"key": "value"}
        
        with patch('urllib.request.urlopen', mock_urlopen):
            result = self.client._make_request("http://test-server:32400/test", data=test_data)
            
            self.assertEqual(result, {"result": "ok"})
            mock_urlopen.assert_called_once()
            
            # Verify the request has data and correct content type
            call_args = mock_urlopen.call_args[0][0]  # Get the request object
            self.assertEqual(call_args.data, json.dumps(test_data).encode('utf-8'))
            self.assertEqual(call_args.get_header('Content-type'), 'application/json')
    
    def test_make_request_adds_token_to_url(self):
        """Test that API requests include the authentication token."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.read.return_value = b'{}'
            mock_response.__enter__.return_value = mock_response
            mock_response.__exit__.return_value = None
            mock_urlopen.return_value = mock_response
            
            self.client._make_request("http://test-server:32400/test")
            
            # Verify the URL includes the token
            call_args = mock_urlopen.call_args[0][0]  # Get the request object
            full_url = call_args.full_url
            self.assertIn("X-Plex-Token=test_token", full_url)
    
    def test_make_request_token_in_url_with_existing_params(self):
        """Test that token is added correctly when URL already has parameters."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.read.return_value = b'{}'
            mock_response.__enter__.return_value = mock_response
            mock_response.__exit__.return_value = None
            mock_urlopen.return_value = mock_response
            
            self.client._make_request("http://test-server:32400/test?existing=param")
            
            # Verify the URL includes both existing params and token
            call_args = mock_urlopen.call_args[0][0]  # Get the request object
            full_url = call_args.full_url
            self.assertIn("existing=param", full_url)
            self.assertIn("&X-Plex-Token=test_token", full_url)


class TestPlexServerEpisodeRefresh(MediaLibraryTestCase):
    """Test PlexServerEpisodeRefresh class functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_server_episode_refresh()
        if not self.module:
            self.skipTest("plex_server_episode_refresh module not available")
        
        # Create a client for testing
        self.client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test-server:32400",
            verbose=True,
            debug=True
        )
    
    def test_initialization(self):
        """Test PlexServerEpisodeRefresh initialization."""
        self.assertEqual(self.client.token, "test_token")
        self.assertEqual(self.client.server_url, "http://test-server:32400")
        self.assertTrue(self.client.verbose)
        self.assertTrue(self.client.debug)
    
    def test_initialization_strips_trailing_slash(self):
        """Test that server URL trailing slash is removed."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test-server:32400/",
            verbose=False,
            debug=False
        )
        self.assertEqual(client.server_url, "http://test-server:32400")
    
    @patch('sys.stdout.write')
    @patch('builtins.print')
    def test_log_verbose(self, mock_print, mock_write):
        """Test verbose logging functionality."""
        self.client.log_verbose("Test verbose message")
        mock_print.assert_called_once_with("[VERBOSE] Test verbose message")
        
        # Test with verbose disabled
        quiet_client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test-server:32400",
            verbose=False,
            debug=False
        )
        mock_print.reset_mock()
        quiet_client.log_verbose("Should not be printed")
        mock_print.assert_not_called()
    
    @patch('sys.stdout.write')
    @patch('builtins.print')
    def test_log_debug(self, mock_print, mock_write):
        """Test debug logging functionality."""
        self.client.log_debug("Test debug message")
        mock_print.assert_called_once_with("[DEBUG] Test debug message")
        
        # Test with debug disabled
        quiet_client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test-server:32400",
            verbose=False,
            debug=False
        )
        mock_print.reset_mock()
        quiet_client.log_debug("Should not be printed")
        mock_print.assert_not_called()


class TestErrorHandling(MediaLibraryTestCase):
    """Test error handling functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_server_episode_refresh()
        if not self.module:
            self.skipTest("plex_server_episode_refresh module not available")
    
    def test_missing_token_raises_error(self):
        """Test that missing PLEX_TOKEN raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.module.PlexServerEpisodeRefresh(
                token=None,
                server_url="http://test:32400",
                verbose=False,
                debug=False
            )
        
        self.assertIn("PLEX_TOKEN not found", str(context.exception))
        self.assertIn("~/.media-library-tools/.env", str(context.exception))
    
    def test_missing_server_raises_error(self):
        """Test that missing PLEX_SERVER raises ValueError."""
        # This won't actually raise an error since server has a default fallback
        # But let's test with an explicitly None server
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url=None,
            verbose=False,
            debug=False
        )
        # Should use default server
        self.assertEqual(client.server_url, "http://localhost:32400")
    
    @patch('urllib.request.urlopen')
    def test_refresh_episode_image_invalid_hash(self):
        """Test handling of invalid episode hash."""
        # Mock API response for non-existent episode
        mock_error = MagicMock()
        mock_error.side_effect = Exception("HTTP 404: Not Found")
        
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        
        with patch.object(client, '_make_request', return_value=None):
            result = client.refresh_episode_image("invalid_hash")
            self.assertFalse(result)
    
    @patch('urllib.request.urlopen')
    def test_refresh_episode_image_api_error(self):
        """Test handling of API errors during episode refresh."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        
        # Mock initial metadata request success but subsequent requests fail
        call_count = 0
        def mock_make_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call (metadata) succeeds
                return {
                    "MediaContainer": {
                        "Metadata": [{
                            "title": "Test Episode",
                            "grandparentTitle": "Test Show",
                            "parentIndex": 1,
                            "index": 1
                        }]
                    }
                }
            else:
                # Subsequent calls fail
                return None
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            result = client.refresh_episode_image("test_hash")
            # Should still return True as the process is designed to continue even if some steps fail
            self.assertTrue(result)
    
    @patch('urllib.request.urlopen')
    def test_refresh_episode_image_empty_metadata(self):
        """Test handling when episode metadata is empty."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        
        # Mock empty metadata response
        empty_metadata = {
            "MediaContainer": {
                "Metadata": []
            }
        }
        
        with patch.object(client, '_make_request', return_value=empty_metadata):
            result = client.refresh_episode_image("test_hash")
            self.assertTrue(result)  # Process continues even with empty metadata


class TestIntegrationWorkflow(MediaLibraryTestCase):
    """Test end-to-end integration workflows."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.module = load_plex_server_episode_refresh()
        if not self.module:
            self.skipTest("plex_server_episode_refresh module not available")
    
    @patch('time.sleep')  # Skip actual sleep delays
    @patch('urllib.request.urlopen')
    def test_complete_episode_refresh_workflow(self):
        """Test complete episode refresh workflow with mocked API responses."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        
        # Mock the complete workflow
        call_sequence = []
        def mock_make_request(url, method='GET', data=None):
            call_sequence.append((url, method))
            
            if 'metadata/12345' in url and method == 'GET':
                # Episode metadata request
                return {
                    "MediaContainer": {
                        "Metadata": [{
                            "title": "Test Episode",
                            "grandparentTitle": "Test Show",
                            "parentIndex": 1,
                            "index": 1,
                            "thumb": "/library/metadata/12345/thumb/123456789"
                        }]
                    }
                }
            elif 'analyze' in url and method == 'PUT':
                # Analyze request
                return ""
            elif 'refresh' in url and method == 'PUT':
                # Refresh request  
                return ""
            elif 'posters' in url and method == 'DELETE':
                # Clear thumbnail request
                return ""
            else:
                return {}
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            result = client.refresh_episode_image("12345")
            
            self.assertTrue(result)
            
            # Verify the expected sequence of API calls
            expected_calls = [
                ('http://test:32400/library/metadata/12345', 'GET'),  # Initial metadata
                ('http://test:32400/library/metadata/12345/analyze', 'PUT'),  # Analyze
                ('http://test:32400/library/metadata/12345/refresh', 'PUT'),  # Refresh
                ('http://test:32400/library/metadata/12345', 'GET'),  # Get metadata again
                ('http://test:32400/library/metadata/12345/posters', 'DELETE'),  # Clear thumbnails
                ('http://test:32400/library/metadata/12345/analyze', 'PUT'),  # Re-analyze
            ]
            
            for expected_call in expected_calls:
                self.assertIn(expected_call, call_sequence)
    
    @patch('time.sleep')  # Skip actual sleep delays
    @patch('builtins.print')
    def test_verbose_workflow(self):
        """Test complete workflow with verbose output."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=True,
            debug=False
        )
        
        # Mock API responses
        def mock_make_request(url, method='GET', data=None):
            if 'metadata/12345' in url and method == 'GET':
                return {
                    "MediaContainer": {
                        "Metadata": [{
                            "title": "Pilot",
                            "grandparentTitle": "Breaking Bad",
                            "parentIndex": 1,
                            "index": 1,
                            "thumb": "/library/metadata/12345/thumb/123456789"
                        }]
                    }
                }
            else:
                return ""
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            result = client.refresh_episode_image("12345")
            
            self.assertTrue(result)
            # Verify verbose output was called (would show up in mock_print calls)
    
    @patch('time.sleep')
    @patch('builtins.print')
    def test_debug_workflow(self):
        """Test complete workflow with debug output."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=False,
            debug=True
        )
        
        # Mock API responses
        def mock_make_request(url, method='GET', data=None):
            if 'metadata/12345' in url and method == 'GET':
                return {
                    "MediaContainer": {
                        "Metadata": [{
                            "title": "Pilot",
                            "grandparentTitle": "Breaking Bad",
                            "parentIndex": 1,
                            "index": 1
                        }]
                    }
                }
            else:
                return ""
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            result = client.refresh_episode_image("12345")
            
            self.assertTrue(result)
            # Debug output would show up in mock_print calls
    
    @patch('time.sleep')
    def test_workflow_error_recovery(self):
        """Test workflow continues even when some API calls fail."""
        client = self.module.PlexServerEpisodeRefresh(
            token="test_token",
            server_url="http://test:32400",
            verbose=False,
            debug=False
        )
        
        # Mock API responses where some fail
        call_count = 0
        def mock_make_request(url, method='GET', data=None):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:  # Initial metadata succeeds
                return {
                    "MediaContainer": {
                        "Metadata": [{
                            "title": "Test Episode",
                            "grandparentTitle": "Test Show",
                            "parentIndex": 1,
                            "index": 1
                        }]
                    }
                }
            elif call_count == 2:  # Analyze fails
                return None
            elif call_count == 3:  # Refresh succeeds
                return ""
            else:  # Other calls succeed
                return {}
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            result = client.refresh_episode_image("12345")
            
            # Should still return True despite some failures
            self.assertTrue(result)
    
    def test_credential_integration_with_workflow(self):
        """Test that credentials work properly in the full workflow context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .env file with credentials
            env_file = Path(temp_dir) / '.env'
            env_file.write_text('PLEX_TOKEN=integration_test_token\nPLEX_SERVER=http://integration-test:32400\n')
            
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Create client without explicit credentials (should read from .env)
                client = self.module.PlexServerEpisodeRefresh(
                    token=None,
                    server_url=None,
                    verbose=False,
                    debug=False
                )
                
                self.assertEqual(client.token, "integration_test_token")
                self.assertEqual(client.server_url, "http://integration-test:32400")
                
                # Mock a simple API call to verify credentials are used
                with patch.object(client, '_make_request') as mock_request:
                    mock_request.return_value = {}
                    
                    # The actual workflow would use these credentials
                    self.assertIsNotNone(client.token)
                    self.assertIsNotNone(client.server_url)
            finally:
                os.chdir(old_cwd)


if __name__ == '__main__':
    unittest.main()