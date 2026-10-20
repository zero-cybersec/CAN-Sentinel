import sys
import platform
import shutil
import importlib.util

def check_environment():
    print("=== Virtual CAN Attack Simulation ===")
    print("Python Version:", sys.version.split()[0])
    print("Operating System:", platform.system())

    print("\nChecking CAN utilities:")

    tools = ["ip", "candump", "cansend"]

    for tool in tools:
        if shutil.which(tool):
            print(f"{tool}: Available")
        else:
            print(f"{tool}: Not found")

    if importlib.util.find_spec("can"):
        print("python-can: Installed")
    else:
        print("python-can: Not installed")

if __name__ == "__main__":
    check_environment()
