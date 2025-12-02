# Election-Voter-Turnout-Dashboard
This project is an interactive Voter Turnout Dashboard built using Python and Dash (Plotly). It visualizes Indian Election data from 10 constituencies across three General Elections (2014, 2019, 2024), providing insights into voter participation trends. 

## 1. Files Provided

- `dashboard.py`  
  Final Python script containing all data processing, visualizations, callbacks, and dashboard layout.

- `1100378_Final_Election_data.xlsx`  
  Curated dataset of 10 constituencies for the 2014, 2019, and 2024 Lok Sabha elections (electors, votes polled, turnout ratios by gender).


## 2. Folder Structure

Place all files in the same folder:

- `dashboard.py`  
- `1100378_Final_Election_data.xlsx`  
- `README.md`  

The script uses a relative path, so the Excel file name and location must match this structure.


## 3. Software Requirements

- Python 3.8 or higher  
- Any modern web browser (Chrome, Edge, Firefox, etc.)

Python libraries (install via `pip`):

- `pandas`  
- `numpy`  
- `dash`  
- `plotly`  
- `openpyxl`  


## 4. One-Time Installation

Open a terminal / command prompt in the folder containing `dashboard.py` and run:

pip install pandas numpy dash plotly
pip install openpyxl


## 5. How to Run the Dashboard

From the same folder (with `dashboard.py` and `1100378_Final_Election_data.xlsx`), run:

python dashboard.py

If successful, the terminal will show a message similar to:
Dash is running on http://127.0.0.1:8050/


## 6. How to Open the Dashboard

1. Open a web browser.  
2. Go to:

http://127.0.0.1:8050/

This loads the interactive dashboard.


## 7. Dashboard Overview

The dashboard reads data from `1100378_Final_Election_data.xlsx` and displays four charts in a 2×2 grid (each chart height ≈ 500px).  
All charts respond to:

- **Select Year** dropdown  
- **Select Constituency** dropdown  
- Some click interactions on chart elements (for drill-down).

### Global Controls

- **Select Year** – chooses the election year (2014, 2019, 2024).  
- **Select Constituency** – chooses one of the 10 constituencies.

These selections are stored internally and used by the callbacks to update all charts.

### Chart 1 – Change in Overall Turnout Ratio Over Time

- **Type:** Line chart with markers.  
- **X-axis:** Year (2014, 2019, 2024).  
- **Y-axis:** Overall turnout ratio (%).  
- **Behavior:**
  - By default, shows weighted overall turnout for all 10 constituencies combined.
  - When a constituency is selected, the line is recomputed only for that constituency.
  - Selecting a year (dropdown or clicking) adds a vertical reference line at that year.
  - Line and markers use the orange palette for visual consistency.

### Chart 2 – Change in Turnout Ratio Across Genders Over Time

- **Type:** Line chart with markers.  
- **Genders:**
  - Male – blue  
  - Female – pink  
- **X-axis:** Year (2014, 2019, 2024).  
- **Y-axis:** Turnout ratio (%).  
- **Behavior:**
  - By default, shows male and female turnout ratios aggregated across all constituencies.
  - When a constituency is selected, male and female lines are recomputed only for that constituency.
  - Year selection adds a vertical reference line.

### Chart 3 – Turnout Distribution Across Constituencies and Time

- **Type:** Grouped bar chart.  
- **X-axis:** Constituency.  
- **Bars:** Overall turnout ratio for each year.
- **Colors (orange palette):**
  - 2014 – `#FDBE85`  
  - 2019 – `#FD8D3C`  
  - 2024 – `#E6550D`  
- **Behavior:**
  - Shows grouped bars per constituency for 2014, 2019, 2024.
  - If a year is selected, bars for that year are emphasized and others can be dimmed.
  - If a constituency is selected, the chart reflects that selection via filtering/highlighting as defined in the callbacks.
  - `categoryorder = "total descending"` ensures constituencies are ordered by total bar height in decreasing order for easier comparison.

### Chart 4 – Turnout Distribution Across Constituencies and Genders

- **Type:** Grouped bar chart with facets by year.  
- **X-axis:** Constituency.  
- **Bars:**
  - Male – blue  
  - Female – pink  
- **Facets:** One panel per year (2014, 2019, 2024).  
- **Behavior:**
  - By default, shows male and female turnout ratios for all constituencies and years.
  - Year and constituency selections filter/highlight the relevant subset.
  - Bars are grouped (not stacked) so that male vs female turnout is directly comparable within each constituency.
  - `categoryorder = "total descending"` is used so constituencies appear in decreasing order of combined bar height within each facet.


## 8. Interaction and Drill-Down

- **Select Year**
  - Updates the shared “selected year” state.
  - Affects x-axis focus and highlighting in all charts.

- **Select Constituency**
  - Updates the shared “selected constituency” state.
  - Recomputes lines in Charts 1 and 2 for that constituency.
  - Filters or emphasizes the constituency in Charts 3 and 4.

- **Chart Clicks**
  - Clicking certain bars or points can also update the selected year and/or selected constituency (depending on the chart), providing a drill-down experience across the four visuals.


## 9. Stopping the App

To stop the dashboard server:

- Go back to the terminal where `python dashboard.py` is running.  
- Press: Ctrl + C

This terminates the Dash app and frees the port.

## Contact Author:

**This Assignment is prepared for Course Data Visualisation and Storytelling, M.Sc. Data Science and AI @ BITS Pilani. Contact author in case of any discrepancy.**

Nikhilesh Kumar 
2025em1100378@bitspilani-digital.edu.in
