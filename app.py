import subprocess

# Define the list of Python files to be executed
python_files = ['indian.py', 'us.py', 'send_email.py']

for python_file in python_files:
    try:
        # Run the Python file
        subprocess.run(['python', python_file], check=True)
        print(f"Successfully ran {python_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {python_file}. Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
