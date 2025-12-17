"""
Violation Examples - Intentionally Broken Code

This file contains clear, fixable violations that CodeTuneStudio should flag.
Each violation is documented with a comment explaining what's wrong.
"""


# VIOLATION 1: Missing input validation
def process_user_data(data):
    """Process user data without validating input structure."""
    user_id = data['user_id']  # No check if key exists
    email = data['email']      # No validation of email format
    age = data['age']          # No type or range validation

    return {
        'id': user_id,
        'contact': email,
        'age': age
    }


# VIOLATION 2: Hardcoded filesystem paths
def save_configuration(config):
    """Save configuration with hardcoded path."""
    path = "/tmp/config.json"  # Hardcoded path - not portable
    with open(path, 'w') as f:
        f.write(str(config))
    return path


# VIOLATION 3: Bare except clause
def fetch_remote_data(url):
    """Fetch data with overly broad exception handling."""
    try:
        import requests
        response = requests.get(url)
        return response.json()
    except:  # Bare except - catches everything including KeyboardInterrupt
        return None


# VIOLATION 4: SQL injection vulnerability
def get_user_by_name(db_connection, username):
    """Query database with string formatting - SQL injection risk."""
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor = db_connection.cursor()
    cursor.execute(query)  # Vulnerable to SQL injection
    return cursor.fetchone()


# VIOLATION 5: Mutable default argument
def add_item(item, item_list=[]):
    """Add item to list with mutable default argument."""
    item_list.append(item)  # Mutable default persists across calls
    return item_list


# VIOLATION 6: No error handling for file operations
def read_config_file(filename):
    """Read configuration file without error handling."""
    with open(filename) as f:  # No check if file exists
        content = f.read()
    return content  # No validation of content format


# VIOLATION 7: Insecure random number generation
def generate_token():
    """Generate security token using non-cryptographic random."""
    import random
    token = ''.join(random.choices('0123456789abcdef', k=32))  # Not cryptographically secure
    return token


# VIOLATION 8: Resource leak - no context manager
def write_log(message, log_file):
    """Write log message without proper resource management."""
    f = open(log_file, 'a')  # File handle not properly closed
    f.write(message + '\n')
    # Missing f.close() or context manager


# VIOLATION 9: Unsafe eval usage
def execute_user_formula(formula, variables):
    """Execute user-provided formula string."""
    return eval(formula, variables)  # Arbitrary code execution risk


# VIOLATION 10: Race condition in file existence check
def safe_write_file(filename, content):
    """Check file existence before writing."""
    import os
    if not os.path.exists(filename):  # Race condition: TOCTOU
        with open(filename, 'w') as f:  # File could be created between check and open
            f.write(content)
