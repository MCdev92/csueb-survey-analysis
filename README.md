# 📚 Student Experience Survey Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Powered%20by-Pandas-lightgrey?logo=pandas&logoColor=black)
![Openpyxl](https://img.shields.io/badge/Excel%20Export-openpyxl-yellowgreen?logo=microsoft-excel&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success)

> This project is a Python-based data processing pipeline designed to ingest raw student experience survey exports and transform them into clean, analyzable datasets. It standardizes inconsistent formats, resolves encoding issues, enriches records with official CRNs by term, and computes key metrics such as mean, median, standard deviation, and response rates.

The final output is a set of well-structured Excel reports that summarize course feedback, faculty performance, and student engagement trends across departments. Designed for institutional research teams, academic leadership, and curriculum committees, the system supports data-driven evaluation and continuous improvement in teaching and learning.

---

## 📂 Project Structure


<pre> 
/eval-data/uni-wide/      # Raw input CSV files
/output/                  # Generated Excel reports
main.py                   # Main analysis script
requirements.txt          # Python libraries needed
README.md                 # Project documentation
</pre>


---

## ⚙️ Features
- ✅ Parses and standardizes raw student survey exports
- ✅ Automatically handles encoding (e.g., UTF-8 / cp1252)
- ✅ Computes:
  - 📊 Mean, Median, and Standard Deviation for scaled responses
  - ✔️ Sums for binary (Yes/No) responses
- ✅ Extracts and merges CRNs using course ID + term
- ✅ Concatenates all open-text feedback using `" | "` delimiter
- ✅ Produces clean, structured Excel outputs using `openpyxl`

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

* Input files must follow the expected format (one row per student response).

* Open-ended feedback is concatenated per course using " | " separator.

* CRNs are dynamically merged based on term + parsed course code.

* Project is modular and easily extensible to accommodate other survey formats or evaluation structures.