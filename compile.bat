cd %~dp0
pyinstaller -y --add-data "/menu";"menu/" --log-level INFO  "main.py"