@echo off

:: --- 1. Start Docker containers ---
echo Starting Docker containers...
docker-compose up -d

:: Wait for a few seconds to ensure the database is ready
timeout /t 10

:: --- 2. Create and activate Python virtual environment ---
echo Creating and activating Python virtual environment...
python -m venv venv
call venv\Scripts\activate

:: --- 3. Install Python dependencies ---
echo Installing Python dependencies from requirements.txt...
pip install -r requiments.txt

:: --- 4. Run the Streamlit application ---
echo Running the Streamlit app...
streamlit run app.py

:: Deactivate the virtual environment (optional, but good practice)
deactivate