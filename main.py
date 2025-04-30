import requests
import logging
import sys
import argparse
from datetime import datetime


# --- Logging Setup ---
# Configures logging to write to a file and the console
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'url_checker.log'

# Handler to write to the file
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8') # 'a' for append
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO) # Minimum level to write to the file

# Handler to write to the console (stderr to avoid interfering with main stdout)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.WARNING) # Show only warnings and errors on the console

# Get the root logger and add handlers
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Overall minimum level
logger.addHandler(file_handler)
logger.addHandler(console_handler) # Also log to console

# --- Main Class ---
class URLChecker:
    def __init__(self) -> None:
        """Initializes the UrlChecker."""
        pass

    def check_site(self, url: str) -> bool:
        """
        Checks the status of a single URL. Returns True if OK, False if failed.
        Logs the result.
        """
        try:
            # Adds http:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            response = requests.get(url, timeout=10) # timeout = 10 seconds

            # Check if status code indicates success (2xx range)
            if 200 <= response.status_code < 300:
                logger.info(f"SUCESS - Status {response.status_code} - URL: {url}")
                return True
            else:
                logger.warning(f"FAILURE - Status {response.status_code} - URL: {url}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"ERROR - {type(e).__name__} - URL: {url}")
            logger.debug(f"Error details for {url}: {e}") # More detailed log
            return False
    

    def process_urls(self, url_list):
        """Processes a list of URLs, counts successes/failures."""
        success_count = 0
        failure_count = 0
        total_count = 0

        logger.info("--- Starting URL checks ---")
        for url in url_list:
            url = url.strip() # Removes leading/trailing whitespace/newlines
            if url: # Skip empty lines
                total_count += 1
                if self.check_site(url):
                    success_count += 1
                else:
                    failure_count += 1
        logger.info(f"--- Checks finished: {success_count} SUCCESS, {failure_count} FAILURE ---")
        return total_count, success_count, failure_count
    

# --- Main Function and Arguments ----
def main():
    parser = argparse.ArgumentParser(description="Checks the status of URLs provided via file or stdin and logs results.")
    parser.add_argument(
        'input_file',
        metavar='URL_FILE', 
        nargs='?', # Makes the argument optional
        type=argparse.FileType('r', encoding='utf-8'), # Opens for reading
        default=sys.stdin, # Defaults to reading from stdin
        help="File containing URLs (one per line). If omitted, reads from standard input."
    )
    args = parser.parse_args()

    checker = URLChecker()

    urls_to_check = []
    logger.info(f"Reading URLs from: {'stdin' if args.input_file is sys.stdin else args.input_file.name}")
    # Reads URLs from file or stdin
    with args.input_file as f:
        urls_to_check = f.readlines()
        
    total, success, failure = checker.process_urls(urls_to_check)

    # Prints a summary to standard output (console)
    print(f"\nCheck Summary:")
    print(f"Total URLs processed: {total}")
    print(f"Successful (2xx Status): {success}")
    print(f"Failures/Errors: {failure}")
    print(f"See the '{log_file}' file for full details.")


if __name__ == "__main__":
    main()
