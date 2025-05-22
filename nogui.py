import sys
import subprocess

if len(sys.argv) != 2:
    print("Usage: python launch.py <spreadsheet_file_or_google_link>")
    sys.exit(1)

path_or_url = sys.argv[1]

subprocess.run(['python', 'extract2.py', path_or_url])
subprocess.run(['python', 'dashboard.py'])
