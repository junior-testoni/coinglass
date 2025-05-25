# TODO List for Coinglass Data Pipeline

This repository currently includes a README with a detailed plan and example code for fetching data from the Coinglass API. Below are the steps needed to turn that plan into a working pipeline. Each item is explained in clear language so you can follow along even if you are not familiar with coding.

1. **Create the Python Script**  
   - Copy the code from the README into a new file named `coinglass_pipeline.py`.  
   - This script contains configuration values such as `API_KEY` and the functions to pull data from Coinglass.
2. **Insert Your API Key**  
   - In the script, find the line that looks like:
     ```python
     API_KEY = "<YOUR_COINGLASS_API_KEY>"  # TODO: Set your Coinglass API key here.
     ```
     Replace `<YOUR_COINGLASS_API_KEY>` with the key you received from Coinglass.  
     (See README line 44 for reference.)
3. **Install Python and Dependencies**  
   - Make sure Python 3 is installed on your computer.  
   - Install the required package by running `pip install requests` from the command line. The other modules (`sqlite3`, `logging`, and `time`) are part of Python itself.
4. **Run the Script**  
   - Execute the script from a terminal with `python coinglass_pipeline.py`.  
   - The script will create a local file named `coinglass_data.db` and start filling it with data.  
   - Running it again in the future will only add new records. (See README lines 376–384 for what the script does and how to schedule it.)
5. **Verify Data**  
   - After running, you can inspect the database with an SQL client or by using the `sqlite3` command-line tool.  
   - Example: `sqlite3 coinglass_data.db "SELECT COUNT(*) FROM open_interest WHERE symbol='BTC';"` (see README line 383).
6. **Optional Future Improvements**  
   - The README suggests expanding to real-time data or additional endpoints if needed.  
   - You can also schedule the script with a cron job so it runs automatically every day.

Following these tasks will get the pipeline up and running so you can collect BTC and ETH derivatives data from Coinglass.

## Progress
- Created `coinglass_pipeline.py` containing the pipeline code.
- Added `requirements.txt` listing required packages.
- Added `.gitignore` to exclude cache and database files from version control.
- Updated `coinglass_pipeline.py` to read the API key from the `COINGLASS_API_KEY` environment variable if available.
- Added a "Setup" section to the README with step-by-step instructions on installing Python, installing dependencies, setting the `COINGLASS_API_KEY` variable, and running the pipeline.
- Next step: follow the new Setup section in the README to configure your environment and execute the script.
