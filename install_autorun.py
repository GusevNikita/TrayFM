import sys
import winreg
from pathlib import Path

KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "TrayFM"


def main():
    script_dir = Path(__file__).parent
    vbs_path = script_dir / "run_trayfm_background.vbs"

    if not vbs_path.exists():
        print(f"Error: {vbs_path} not found")
        return 1

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, str(vbs_path))
        winreg.CloseKey(key)
        print(f"Autorun added: {vbs_path}")
        print("TrayFM will start automatically when you log in.")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
