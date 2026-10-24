$reg = "HKLM\Software\Python\PythonCore\3.14\InstallPath"

# Back up the registration
reg export "HKLM\Software\Python\PythonCore\3.14" "$env:TEMP\python314-backup.reg" /y

# Correct the three paths
reg add $reg /ve /t REG_SZ /d "C:\python\python314" /f
reg add $reg /v ExecutablePath /t REG_SZ /d "C:\python\python314\python.exe" /f
reg add $reg /v WindowedExecutablePath /t REG_SZ /d "C:\python\python314\pythonw.exe" /f

# Fix pip paths
py -3.14 -m pip install --force-reinstall --no-deps pip