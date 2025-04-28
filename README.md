# 📚 Student Experience Survey Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Powered%20by-Pandas-lightgrey?logo=pandas&logoColor=black)
![Openpyxl](https://img.shields.io/badge/Excel%20Export-openpyxl-yellowgreen?logo=microsoft-excel&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success)

> A Python-based data processing pipeline to clean, transform, and analyze student survey results. Outputs polished Excel reports summarizing course evaluations, instructor feedback, and statistical performance across departments.

---

## 📂 Project Structure

/eval-data/uni-wide/      # Raw input CSV files
/output/                  # Generated Excel reports
main.py                   # Main analysis script
requirements.txt          # Python libraries needed
README.md                 # Project documentation


---

## ⚙️ Features

- ✅ Parses and cleans raw student experience survey data
- ✅ Computes:
  - Mean, Median, Standard Deviation for scaled questions
  - Sum for binary (Yes/No) responses
- ✅ Concatenates all open-text feedback responses
- ✅ Removes inconsistent question numbering
- ✅ Outputs clean, formatted Excel reports
- ✅ Handles file encoding issues automatically

---

## 🚀 Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/student-experience-survey-analysis.git
   cd student-experience-survey-analysis

2. **Setup Virtual Environment:**
python -m venv .venv
source .venv/bin/activate   # (Linux/macOS)
.venv\Scripts\activate      # (Windows)

3. **Install Required Packages:**
pip install -r requirements.txt

## 🧠 Notes

* Ensure input files match expected formatting (one row per student response).

* All text feedback comments are concatenated into a single field separated by " | ".

* Project is easily extendable for future survey structures or new evaluation forms.