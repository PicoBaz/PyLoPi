import re
import requests
from bs4 import BeautifulSoup
import json
from email_notifier import EmailNotifier


class LogAnalyzer:
    def __init__(self, database, config):
        self.db = database
        self.config = config
        self.email_notifier = EmailNotifier(config)

        self.error_patterns = {
            'SyntaxError': r'SyntaxError:(.+)',
            'TypeError': r'TypeError:(.+)',
            'ValueError': r'ValueError:(.+)',
            'AttributeError': r'AttributeError:(.+)',
            'NameError': r'NameError:(.+)',
            'ImportError': r'ImportError:(.+)',
            'IndexError': r'IndexError:(.+)',
            'KeyError': r'KeyError:(.+)',
            'FileNotFoundError': r'FileNotFoundError:(.+)',
            'PermissionError': r'PermissionError:(.+)',
            'RuntimeError': r'RuntimeError:(.+)',
            'MemoryError': r'MemoryError:(.+)',
            'RecursionError': r'RecursionError:(.+)',
            'ZeroDivisionError': r'ZeroDivisionError:(.+)',
            '404Error': r'(404|Not Found)',
            '500Error': r'(500|Internal Server Error)',
            '403Error': r'(403|Forbidden)',
            'DatabaseError': r'(database|sql|mysql|postgres).*error',
            'ConnectionError': r'(connection|network).*error',
            'TimeoutError': r'timeout',
        }

    def analyze_log_line(self, line, log_file):
        detected_error = self.detect_error(line)

        if not detected_error:
            return

        error_type, error_message = detected_error

        if not self.should_process_error(error_type):
            return

        analysis = self.generate_analysis(error_type, error_message, line)
        solution = self.search_solution(error_type, error_message)
        code_fix = self.generate_code_fix(error_type, error_message, line)
        severity = self.determine_severity(error_type)

        log_data = {
            'log_file': log_file,
            'error_type': error_type,
            'error_message': error_message,
            'full_log': line,
            'analysis': analysis,
            'solution': solution,
            'code_fix': code_fix,
            'severity': severity
        }

        log_id = self.db.insert_log(log_data)

        if self.config.get('email_notifications', False):
            self.email_notifier.send_notification(log_id, log_data)

    def detect_error(self, line):
        for error_type, pattern in self.error_patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                error_message = match.group(1) if match.groups() else match.group(0)
                return error_type, error_message.strip()
        return None

    def should_process_error(self, error_type):
        enabled_errors = self.config.get('enabled_error_types', [])
        if not enabled_errors:
            return True
        return error_type in enabled_errors

    def generate_analysis(self, error_type, error_message, full_log):
        analyses = {
            'SyntaxError': f'Syntax error detected in the code. The error message indicates: {error_message}. This typically means there is a typo, missing punctuation, or incorrect indentation in your code.',
            'TypeError': f'Type mismatch error: {error_message}. This occurs when an operation is performed on incompatible data types.',
            'ValueError': f'Invalid value error: {error_message}. The function received an argument of the correct type but inappropriate value.',
            'AttributeError': f'Attribute access error: {error_message}. An object does not have the attribute or method being accessed.',
            'NameError': f'Name reference error: {error_message}. A variable or function name is used before being defined.',
            'ImportError': f'Module import error: {error_message}. The specified module or package cannot be found or imported.',
            'IndexError': f'Index out of range: {error_message}. Attempting to access a list/array index that does not exist.',
            'KeyError': f'Dictionary key error: {error_message}. Trying to access a dictionary key that does not exist.',
            'FileNotFoundError': f'File not found: {error_message}. The specified file path does not exist.',
            '404Error': 'HTTP 404 Not Found error. The requested resource could not be found on the server.',
            '500Error': 'HTTP 500 Internal Server Error. The server encountered an unexpected condition.',
            'DatabaseError': f'Database operation failed: {error_message}. Check database connection and query syntax.',
            'ConnectionError': f'Network connection failed: {error_message}. Check network connectivity and service availability.',
        }

        return analyses.get(error_type, f'Error detected: {error_type} - {error_message}')

    def search_solution(self, error_type, error_message):
        try:
            query = f"{error_type} {error_message[:50]}"
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                snippets = soup.find_all('div', class_='BNeawe')

                solutions = []
                for snippet in snippets[:3]:
                    text = snippet.get_text()
                    if text and len(text) > 50:
                        solutions.append(text)

                if solutions:
                    return '\n\n'.join(solutions)
        except:
            pass

        return self.get_default_solution(error_type)

    def get_default_solution(self, error_type):
        solutions = {
            'SyntaxError': 'Check for missing colons, parentheses, or quotes. Verify proper indentation.',
            'TypeError': 'Ensure all variables are of the expected type. Use type conversion functions if needed.',
            'ValueError': 'Validate input values before processing. Use try-except blocks for error handling.',
            'AttributeError': 'Check if the object has the attribute. Use hasattr() to verify before accessing.',
            'NameError': 'Make sure all variables are defined before use. Check for typos in variable names.',
            'ImportError': 'Install the required package using pip. Verify the module name is correct.',
            'IndexError': 'Check list bounds before accessing. Use len() to verify index is within range.',
            'KeyError': 'Use .get() method or check if key exists before accessing dictionary.',
            'FileNotFoundError': 'Verify the file path is correct. Use os.path.exists() to check file existence.',
            '404Error': 'Check the URL is correct. Verify the resource exists on the server.',
            '500Error': 'Check server logs for details. Review recent code changes.',
            'DatabaseError': 'Verify database connection parameters. Check SQL query syntax.',
            'ConnectionError': 'Check network connectivity. Verify service is running and accessible.',
        }

        return solutions.get(error_type, 'Review the error message and stack trace for specific details.')

    def generate_code_fix(self, error_type, error_message, full_log):
        fixes = {
            'SyntaxError': 'if condition:\n    pass\n\nfor item in items:\n    process(item)',
            'TypeError': 'value = str(value)\nresult = int(input("Enter number: "))',
            'ValueError': 'try:\n    value = int(user_input)\nexcept ValueError:\n    print("Invalid input")',
            'AttributeError': 'if hasattr(obj, "attribute"):\n    result = obj.attribute',
            'NameError': 'variable_name = "value"\nresult = variable_name',
            'IndexError': 'if 0 <= index < len(my_list):\n    item = my_list[index]',
            'KeyError': 'value = my_dict.get("key", default_value)',
            'FileNotFoundError': 'import os\nif os.path.exists(filepath):\n    with open(filepath) as f:\n        data = f.read()',
            'DatabaseError': 'try:\n    cursor.execute(query)\n    conn.commit()\nexcept Exception as e:\n    conn.rollback()\n    print(f"Error: {e}")',
        }

        return fixes.get(error_type, '')

    def determine_severity(self, error_type):
        critical = ['500Error', 'DatabaseError', 'MemoryError', 'RecursionError']
        high = ['TypeError', 'AttributeError', 'ImportError', 'ConnectionError']
        medium = ['ValueError', 'KeyError', 'IndexError', '404Error']
        low = ['SyntaxError', 'NameError']

        if error_type in critical:
            return 'critical'
        elif error_type in high:
            return 'high'
        elif error_type in medium:
            return 'medium'
        else:
            return 'low'