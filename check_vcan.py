import subprocess

def check_vcan():
    print("=== Virtual CAN Interface Check ===")

    try:
        result = subprocess.run(
            ["ip", "link", "show", "vcan0"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("vcan0 interface found.")
            print(result.stdout)
        else:
            print("vcan0 is not available.")
            print("Set up vcan0 on a Linux system first.")

    except FileNotFoundError:
        print("The 'ip' command is unavailable.")
        print("Run this check on a Linux environment.")

if __name__ == "__main__":
    check_vcan()
