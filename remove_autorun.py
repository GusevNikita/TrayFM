import sys
import winreg

KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "TrayFM"


def main():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, VALUE_NAME)
            print("Autorun removed.")
        except FileNotFoundError:
            print("Autorun was not set.")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
