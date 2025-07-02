#!/usr/bin/env python                # Shebang line to specify the Python interpreter
"""Django's command-line utility for administrative tasks."""  # Module docstring describing the file's purpose
import os                            # Import the os module for environment variable operations
import sys                           # Import the sys module for command-line arguments

def main():                          # Define the main function
    """Run administrative tasks."""  # Docstring for the main function
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renthive.settings')  # Set default Django settings module if not already set
    try:
        from django.core.management import execute_from_command_line  # Import Django's command-line execution utility
    except ImportError as exc:       # Handle ImportError if Django is not installed
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "  # Error message if Django can't be imported
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)  # Execute the command-line utility with system arguments

if __name__ == '__main__':           # Check if the script is run as the main program
    main()                           # Call the main function
