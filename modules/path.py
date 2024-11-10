import os
import platform
import sys
import winreg as reg

def set_env_variable(name, value):
    try:
        # Check the platform (Operating System)
        current_platform = platform.system()

        # For Windows
        if current_platform == "Windows":
            set_windows_env_variable(name, value)

        # For Linux or macOS
        elif current_platform in ["Linux", "Darwin"]:
            set_linux_mac_env_variable(name, value)

        else:
            print(f"Unsupported platform: {current_platform}")

    except Exception as e:
        print(f"Error: {e}")

def set_windows_env_variable(name, value):
    import winreg as reg
    try:
        # Open the registry key for environment variables
        reg_key = reg.HKEY_CURRENT_USER
        reg_path = r"Environment"

        # Open the registry key for writing
        with reg.OpenKey(reg_key, reg_path, 0, reg.KEY_WRITE) as key:
            # Set the environment variable
            reg.SetValueEx(key, name, 0, reg.REG_SZ, value)

        print(f"Environment variable {name} set to {value} successfully!")

    except Exception as e:
        print(f"Error setting Windows environment variable: {e}")
        print("Try running as administrator if you encounter issues.")

def set_linux_mac_env_variable(name, value):
    try:
        # Define the shell config file (bash or zsh)
        shell_config_file = os.path.expanduser("~/.bashrc")  # Use ~/.zshrc for Zsh

        # Ensure the export statement is only added once
        export_line = f'export {name}="{value}"\n'

        # Read the existing file and check if the export line exists
        with open(shell_config_file, "r") as file:
            lines = file.readlines()

        if export_line not in lines:
            # Append the export line to the config file
            with open(shell_config_file, "a") as file:
                file.write(export_line)
            print(f"Environment variable {name} set to {value} successfully!")
        else:
            print(f"Environment variable {name} already exists in {shell_config_file}.")

        # Suggest the user to reload the shell configuration
        print("To apply the change, run 'source ~/.bashrc' (or 'source ~/.zshrc' for Zsh).")

    except Exception as e:
        print(f"Error setting Linux/macOS environment variable: {e}")

def check_windows_env_variable(name):
    try:
        # Open the registry key for environment variables
        reg_key = reg.HKEY_CURRENT_USER
        reg_path = r"Environment"

        # Open the registry key for reading
        with reg.OpenKey(reg_key, reg_path, 0, reg.KEY_READ) as key:
            try:
                # Try to read the environment variable
                value, _ = reg.QueryValueEx(key, name)
                return value
            except FileNotFoundError:
                print(f"{name} not found, please enter your:")

    except Exception as e:
        print(f"Error reading from registry: {e}")

def yieldGetPath(original = None):
    while True:
        apiKey = original != None and original or check_windows_env_variable("XAI_API_KEY")
        if (apiKey and original != None):
            break
        else:
            enteredKey = input("Please enter your own XAI_API_KEY: ")
            if (original != None and not enteredKey.strip()):
                print("🔐 Using last entered API Key ✅")
                break
            elif (not enteredKey.startswith("xai")):
                print("Please enter a valid xai key. It should look something like this, starting with xai: \"xai-AAAAAAAAAAAAAAAAAAAAAAAAAAA\"")
            else:
                set_env_variable("XAI_API_KEY", enteredKey)
                apiKey = enteredKey
                #print("🔑 Key validated! It is saved if you are on PC!")
                break
    return apiKey