#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Install all dependencies from requirements.txt
echo "--- Installing dependencies ---"
pip install -r lottery_scraper/requirements.txt

# Run the scraper to update the data
echo "--- Scraping for latest results ---"
python3 lottery_scraper/scraper.py

# Run the HTML generator to build the page
echo "--- Generating HTML page ---"
python3 lottery_scraper/generate_html.py

echo "--- Build complete ---"
