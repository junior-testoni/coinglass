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
- Next step: set your API key via the environment variable or directly in the script, then run `pip install -r requirements.txt` before executing the pipeline.
- Cleaned README title and removed stale content references.
- Next step: review pipeline code and run tests.
- Added a simple `pytest` test and documented how to run it.
- Added `.vscode/` to `.gitignore` so editor settings are not tracked.
- Next step: set your API key via the environment variable or directly in the script,
  then run `pip install -r requirements.txt` and `pytest` before executing the pipeline.
- Updated `AGENTS.md` to note that `coinglass_pipeline.py` now implements the pipeline.
- Next step: verify all documentation remains consistent with the code.
- Added a list of additional endpoints and a generic fetch method to
  `coinglass_pipeline.py`. Also created `coinglass_endpoints.py` and
  documented these endpoints in the README.
  Next step: try fetching some of the new endpoints and review the stored data.

- Added docstrings and optional ``start_time``/``end_time`` parameters to all
  fetch methods in ``coinglass_pipeline.py`` so you can limit the date range
  when calling an endpoint.
  Next step: run ``pytest`` to ensure the script still imports correctly.


- Updated `coinglass_pipeline.py` to fetch every endpoint listed in `coinglass_endpoints.py` and store the JSON results.
  Next step: run the pipeline with your API key to review the collected data

- Changed `BASE_URL` in both the README and `coinglass_pipeline.py` so the API
  calls point to `https://open-api-v4.coinglass.com` without an extra `/api`
  segment. This prevents requests to URLs like `/api/api/...`.
  Next step: run `pytest -q` then run the pipeline to confirm the endpoints work.

- Fixed endpoint URLs in `coinglass_pipeline.py` so core API calls use the
  documented paths with `/api` and the generic fetch method no longer builds
  malformed URLs. Updated the loop over `ADDITIONAL_ENDPOINTS` accordingly.
  Next step: execute `pytest -q` and run the pipeline to verify data downloads
  succeed.

- Added a simple rate limiter to `CoinglassClient` so each request waits at
  least two seconds. This keeps the pipeline under the Hobbyist limit of 30
  requests per minute.
  Next step: run `pytest -q` and run the pipeline to confirm no rate limit

- Limited additional endpoint fetching to a subset (`DEFAULT_ADDITIONAL_ENDPOINTS`)
  that works without extra parameters. Update this list if you need more data.

