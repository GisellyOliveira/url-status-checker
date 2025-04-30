# ✨ URL Status Checker (Python) ✨

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quickly check the health of your link lists!**

Tired of finding broken links in your projects, documents, or lists? This robust and well-tested command-line tool, developed in Python, **solves this problem** by efficiently checking the HTTP status of a list of URLs. Automate link validation and ensure your online resources are always accessible. Ideal for **quick monitoring**, **sitemap validation**, **cleaning up bookmark lists**, or any situation where the integrity of multiple links needs to be confirmed.

This project demonstrates not only the core functionality but also the application of development best practices, including detailed logging, error handling, and crucially, **comprehensive unit and integration tests with extensive use of mocking**.

## 🚀 Key Features

*   **HTTP Status Check:** Uses the `requests` library to make GET requests and determine if a URL is accessible (2xx status).
*   **Flexible Input:** Accepts a list of URLs (one per line) from both a text file and directly from standard input (`stdin`), allowing easy integration with other scripts or commands via pipe (`|`).
*   **Configurable Output:** Displays a concise summary on standard output (`stdout`) and logs detailed results to a log file (defaults to `site_checker.log`).
*   **Robust Logging:** Implements Python's standard `logging` module to record SUCCESS, FAILURE (non-2xx status), and ERROR events (timeouts, connection problems), with timestamps and severity levels. Logs are directed to a file and optionally to the console (`stderr`).
*   **Error Handling:** Catches common exceptions from the `requests` library, such as timeouts and other connection errors, logging them appropriately.
*   **Clear Command-Line Interface (CLI):** Uses `argparse` to provide a simple and intuitive user interface with options for specifying input files.
*   **Tested Code:** Accompanied by a detailed test suite using `unittest` and `unittest.mock` to ensure reliability and facilitate maintenance. **Mocking is used extensively** to isolate tests from external network dependencies.

## 🛠️ Technologies Used

*   **Python 3.9+**
*   **Standard Libraries:**
    *   `sys`: Access to stdin/stdout/stderr.
    *   `argparse`: Command-line argument parsing.
    *   `logging`: Flexible logging system.
    *   `datetime`: Date/time manipulation (used by logging).
    *   `unittest` & `unittest.mock`: Testing framework and mocking tools.
    *   `io`: Simulation of text streams for testing.
*   **External Libraries:**
    *   `requests`: Making HTTP requests.

## ⚙️ Installation

1.  Clone the repository:
    ```
    git clone https://github.com/GisellyOliveira/url-status-checker.git
    ```

2.  (Optional, but recommended) Create and activate a virtual environment:
    ```
    cd url-status-checker
    python -m venv .venv
    # On Windows:
    .\.venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## 💻 How to Use

Execute the `main.py` script from your terminal.

### 1. Reading URLs from Keyboard (Standard Input)
Execute the command:

```
python main.py
```

Enter the URLs (one per line) and press Ctrl+D (Linux/macOS) or Ctrl+Z+Enter (Windows) when finished. The summary will be displayed on the screen, and the details in the log file.

### 2. Reading URLs from a File
Create a file (e.g., my_urls.txt) with one URL per line. Execute:

```
python main.py my_urls.txt
```

The summary will be displayed on the screen, and the details in the log file.

### 3. Reading from a File and Saving Log Elsewhere (Advanced Example - Requires Code Modification to accept --logfile)
(Note: The current code has a fixed log file name. Adding a --logfile argument would be a future enhancement.)

### 4. Using Pipe
You can pipe the output of another command that lists URLs directly into the script:
```cat my_urls.txt | python main.py```

The summary will be displayed on the screen, and the full details will be logged in the site_checker.log file.

## ✅ Testing the Tool
The code's quality and reliability are ensured by an automated test suite located in *test_main.py.* The tests extensively use mocking to simulate network requests (requests.get) and interactions with the filesystem/IO (sys.stdin, sys.stdout, open), ensuring that the tests are fast, deterministic, and do not depend on external services or the network.

To run the tests:
Navigate to the project's root directory in your terminal and execute:
```
python -m unittest test_main.py -v
```
The -v (verbose) flag shows details about each test executed. You should see all tests passing with OK.

## 📂 Code Structure

* **main.py:** The main script containing the tool's logic (class VerificadorUrl and function main).
* **test_main.py:** Contains the unit and integration tests using unittest and unittest.mock.
* **site_checker.log:** Log file automatically generated by the tool (ignored by Git via .gitignore).
* **requirements.txt:** Lists external dependencies (only requests).
* **README.md:** This file.
* **.gitignore:** File instructing Git to ignore certain files (like *.log and __pycache__/).

## 🚀 Future Improvements (Possible)
* Add a command-line argument (--logfile) to specify a different name/path for the log file.
* Implement asynchronous checking (asyncio, aiohttp) to check multiple URLs in parallel, making the tool much faster for large lists.
* Add an option to configure the request timeout via argument (--timeout).
* Allow different HTTP methods (HEAD, POST, etc.) via argument (--method).
* Option to define the number of retries in case of failure (--retries).
* Output the summary in structured formats like JSON or CSV (--output-format).
* Better handling of HTTP redirects (option --follow-redirects).

## 📄 License
This project is licensed under the MIT License. See the LICENSE file (if it exists) for more details.

👤 Contact
Created by *Giselly Oliveira* - **Email:** *gioliveira@protonmail.com*