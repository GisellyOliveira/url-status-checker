import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call # MagicMock to simulate the requests response
import logging
import requests
import sys
import io # To simulate stdin if necessary

# Imports the class and main function from the original script
from main import URLChecker, main, log_file # Also import log_file for reference


class TestUrlChecker(unittest.TestCase):
    """Tests for the UrlChecker tool."""

    def setUp(self) -> None:
        """Creates a fresh checker instance before each test."""
        self.checker = URLChecker()
        # Cleans up simulated log content before each test (if necessary)
        # Not simulating the log file directly here, but capturing.


    # --- Tests for the check_site method in isolation ---

    @patch('main.requests.get') # Mock the get function INSIDE the main module
    def test_check_site_success(self, mock_get):
        """Tests the success case (200 status)."""
        # Setup mock to return an OK response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Use assertLogs to capture what was logged during the call
        with self.assertLogs(level='INFO') as log_context:
            result = self.checker.check_site("https://google.com")

        self.assertTrue(result)

        # Verify the method returned True
        mock_get.assert_called_once_with("https://google.com", timeout=10)
        # Verify the correct SUCCESS log message was logged
        self.assertIn("INFO:root:SUCCESS - Status 200 - URL: https://google.com", log_context.output)


    @patch('main.requests.get')
    def test_check_site_failure_404(self, mock_get):
        """Tests the failure case (404 status)."""
        # Setup mock to return a 404 Not Found response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Capture INFO and above
        with self.assertLogs(level='INFO') as log_context:
            result = self.checker.check_site("http://nonexistent123.com")

        self.assertFalse(result)
        mock_get.assert_called_once_with("http://nonexistent123.com", timeout=10)
        # Verify the correct FAILURE log message was logged (WARNING level)
        self.assertIn("WARNING:root:FAILURE - Status 404 - URL: http://nonexistent123.com", log_context.output)


    @patch('main.requests.get')
    def test_check_site_error_timeout(self, mock_get):
        """Tests the error case (Timeout)."""
        # Setup mock to raise a Timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out!")

        with self.assertLogs(level='INFO') as log_context:
            result = self.checker.check_site("http://slowsite.com")

        self.assertFalse(result)
        mock_get.assert_called_once_with("http://slowsite.com", timeout=10)
        # Verify the correct ERROR log message was logged
        self.assertIn("ERROR:root:ERROR - Timeout - URL: http://slowsite.com", log_context.output)


    @patch('main.requests.get')
    def test_check_site_adds_http_scheme(self, mock_get):
        """
        Tests if http:// scheme is added if missing and logs DEBUG message
        when logger level is adjusted.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # --- Temporary Log Level Adjustment ---
        # Get the root logger and save original level to restore later
        root_logger = logging.getLogger() # get the root logger
        original_level = root_logger.getEffectiveLevel()
        # Set level to DEBUG before calling the method under test
        root_logger.setLevel(logging.DEBUG)
        # Ensure original level is restored after the test, even if it fails
        self.addCleanup(root_logger.setLevel, original_level)

        # --- Execution and Log Capture ---
        # Use assertLogs to capture messages starting from DEBUG level
        with self.assertLogs(level='DEBUG') as log_context: # Capture DEBUG
            # Call the method with a URL without the http/https scheme
            self.checker.check_site("google.com")

        # Check if requests.get was called with http:// added
        mock_get.assert_called_once_with("http://google.com", timeout=10)
        # Note: Original code provided did not assert the DEBUG log message here.


    # --- Tests for the process_urls method ---

    # Mock the check_site method WITHIN the test class itself
    # to avoid depending on the requests.get mock again here
    @patch.object(URLChecker, 'check_site', autospec=True)
    def test_process_urls_counts(self, mock_check_site_internal):
        """Tests the success/failure counts in process_urls."""

        # Define internal mock behavior: return True for google, False otherwise
        # The first arg is the instance (self)
        def check_side_effect(instance_self, url):
            if "google" in url:
                return True
            else:
                return False
        mock_check_site_internal.side_effect = check_side_effect

        test_urls = [
            "google.com\n",       # Success
            "  badsite.com  ",    # Failure
            "",                   # Empty line should be ignored
            "https://google.com", # Success
            "http://failed.org"   # Failure
        ]

        with self.assertLogs(level='INFO') as log_context:
            total, success, failure = self.checker.process_urls(test_urls)

        # Check counts
        # Assertion messages translated
        self.assertEqual(total, 4, "Incorrect total count of non-empty URLs.")
        self.assertEqual(success, 2, "Incorrect success count.")
        self.assertEqual(failure, 2, "Incorrect failure count.")

        # Check if internal mock calls were made correctly
        # Called 4 times (skips empty)
        self.assertEqual(mock_check_site_internal.call_count, 4)
        # Check specific calls
        mock_check_site_internal.assert_any_call(self.checker, "google.com")
        mock_check_site_internal.assert_any_call(self.checker, "badsite.com")
        mock_check_site_internal.assert_any_call(self.checker, "https://google.com")
        mock_check_site_internal.assert_any_call(self.checker, "http://failed.org")

        # Check start/end logs
        self.assertIn("INFO:root:--- Starting URL checks ---", log_context.output)
        self.assertIn("INFO:root:--- Checks finished: 2 SUCCESS, 2 FAILURE ---", log_context.output)


# --- Test for the main function (Integration Test) ---
# Mock more things here to simulate the full execution

# Use multiple patches: stdin, stdout, requests.get, and argparse
# Capture stdout
@patch('sys.stdout', new_callable=io.StringIO)
# Mock requests
@patch('main.requests.get')
# Mock argument parsing
@patch('argparse.ArgumentParser.parse_args')
# Simulate stdin
@patch('sys.stdin', new_callable=io.StringIO)
class TestMainFunction(unittest.TestCase):

    def test_main_with_stdin(self, mock_stdin, mock_parse_args, mock_requests_get, mock_stdout):
        """Tests the main flow reading from simulated stdin."""

        # 1. Setup Mocks:
        # Simulate user input in stdin
        mock_stdin.write("ok.com\n")
        mock_stdin.write("bad.com\n")
        # Rewind the simulated stdin "file"
        mock_stdin.seek(0)

        # Simulate arguments returned by argparse (as if no file was passed)
        # Needs to return an object with 'input_file' attribute pointing to mocked stdin
        args_mock = MagicMock()
        args_mock.input_file = mock_stdin
        mock_parse_args.return_value = args_mock

        # Configure the requests.get mock (similar to previous tests)
        def side_effect_get(url, timeout):
            response = MagicMock()
            if "ok.com" in url:
                response.status_code = 200
            else:
                response.status_code = 500 # Simulate a server error
            return response
        mock_requests_get.side_effect = side_effect_get

        # 2. Execute main function
        # Use assertLogs to capture logs during main's execution
        with self.assertLogs('root', level='INFO') as log_context:
            # Call imported main function
            main()

        # 3. Verify Outputs
        # Check summary printed to simulated stdout
        output = mock_stdout.getvalue()
        # Assertions translated and adjusted to match main.py output
        self.assertIn("Check Summary:", output)
        self.assertIn("Total URLs processed: 2", output)
        self.assertIn("Successful (2xx Status): 1", output)
        self.assertIn("Failures/Errors: 1", output)
        self.assertIn(f"See the '{log_file}' file for full details.", output)

        # Check important logs
        self.assertIn("INFO:root:SUCCESS - Status 200 - URL: http://ok.com", log_context.output)
        self.assertIn("WARNING:root:FAILURE - Status 500 - URL: http://bad.com", log_context.output)
        self.assertIn("INFO:root:--- Checks finished: 1 SUCCESS, 1 FAILURE ---", log_context.output)


# Script Entry Point
if __name__ == '__main__':
    unittest.main(verbosity=2)
    