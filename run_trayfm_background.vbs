Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "pythonw.exe -u """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\trayfm.py""", 0, False
