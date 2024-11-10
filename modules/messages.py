import pathlib
import re
import pathlib
import platform
import sys

# ANSI escape codes for rich text formatting
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"  # Resets all styles

def get_latest_message(messagesRoot):
    most_recent_file = None
    most_recent_time = 0  # Use 0 as the initial comparison value

    # Iterate over all files in the directory
    for file in messagesRoot.iterdir():
        if file.is_file():  # Ensure it's a file, not a directory
            # Get the modification time of the file
            file_mod_time = file.stat().st_mtime

            # Check if this file is more recently modified than the current most recent file
            if file_mod_time > most_recent_time:
                most_recent_time = file_mod_time
                most_recent_file = file

    if most_recent_file:
        #print(f"The most recently modified file is: {most_recent_file}")
        return most_recent_file
    else:
        #print("No files found in the directory.")
        return False

def get_all_messages(messagesRoot):
    messageNames = []
    for file in (messagesRoot).iterdir():
            if file.is_file():  # Ensure it's a file, not a directory
                messageNames.append(file.stem.replace("_", " "))
    return messageNames

def is_valid_filename(filename):
    try:
        pathlib.Path(filename).touch()
        pathlib.Path(filename).unlink()
        return True
    except OSError:
        return False

def addPersonPreface(is_model: bool):
    if is_model:
        sys.stdout.write(f"{GREEN}grok: {RESET}")
    else:
        sys.stdout.write(f"{RED}>> {RESET}")

def createMessages(build_path: pathlib.Path):
    if not (build_path / "messages").exists():
        (build_path / "messages").mkdir()

# TEST_CODE

#build_path = pathlib.Path(__file__).resolve().parent.parent

## Define the path to the 'messages' directory
#messages_path = build_path / "messages"

#get_latest_message(messages_path)
