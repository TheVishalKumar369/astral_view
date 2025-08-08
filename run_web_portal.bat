@echo off
REM Activate virtual environment and start the web portal (React app)
cd web_portal
call ..\venv\Scripts\activate
npm install
npm start
REM The web portal will be available at http://localhost:3000
echo Web portal exited.
