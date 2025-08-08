@echo off
REM Activate virtual environment and run data-related scripts
call .\venv\Scripts\activate
python scripts\collect_data.py
python scripts\process_data.py
REM Add more data scripts as needed
echo Data scripts completed.
