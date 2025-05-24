# AGENTS Instructions for coinglass Repository

This repository currently contains only a README detailing a plan for a Bitcoin and Ethereum data pipeline using the Coinglass API. There is no actual code yet.

These instructions are aimed at other assistants or developers (with or without coding experience) who may work on this repository.

## Goals
- Implement a Python pipeline that downloads open interest, funding rate, long/short ratio, and liquidation data for BTC and ETH from the Coinglass API.
- Store data in a local SQLite database.

## How to Contribute
1. Use Python 3 for all scripts.
2. Keep code in simple `.py` files with clear names.
3. Include comments and docstrings explaining what each function does so someone without coding experience can understand the overall workflow.
4. If external libraries are required, add them to a `requirements.txt` file.

## Running Code
- Ensure you have Python 3 installed.
- Install required libraries using `pip install -r requirements.txt`.
- Execute the main script (e.g., `python coinglass_pipeline.py`).

## Pull Requests
When creating pull requests:
- Summarize what you added or changed in plain language.
- Mention any placeholders or steps that still need work.
- Provide basic testing instructions if applicable.

