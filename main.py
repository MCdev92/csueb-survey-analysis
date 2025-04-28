#!/usr/bin/env python3
import pandas as pd
import glob
import os
import re
import numpy as np

# === Department code to full name mapping ===
dept_map = {
    'ASTR': 'Astronomy', 'BIOL': 'Biological Sciences', 'BSTA': 'Biostatistics',
    'CMGT': 'Construction Management', 'CMPE': 'Computer Engineering', 'CS': 'Computer Science',
    'ENGR': 'Engineering', 'ENSC': 'Environmental Science', 'GEOL': 'Geology',
    'INDE': 'Industrial Engineering', 'MATH': 'Mathematics', 'MUS': 'Music',
    'NURS': 'Nursing', 'PH': 'Public Health', 'PHYS': 'Physics', 'PSYC': 'Psychology',
    'SCI': 'Science', 'STAT': 'Statistics', 'CIVE': 'Civil Engineering', 'CHEM': 'Chemistry'
}

# 1. Locate all survey exports
data_folder = '/Users/student/Documents/survey-data/eval-data/uni-wide'
output_folder = 'transformation' 
pattern = os.path.join(data_folder, '*StudentExperienceSurvey*.csv')
all_files = [f for f in glob.glob(pattern) if not os.path.basename(f).startswith('sample_cos_report')]
if not all_files:
    raise FileNotFoundError(f"No CSVs found in {data_folder} matching pattern")

# 2. Read & concatenate (with cp1252 fallback)
df_list = []
for fpath in all_files:
    try:
        df_list.append(pd.read_csv(fpath, encoding='utf-8'))
    except UnicodeDecodeError:
        df_list.append(pd.read_csv(fpath, encoding='cp1252', engine='python'))

df = pd.concat(df_list, ignore_index=True)

# 3. Standardize column names and filter to CSCI
df.columns = df.columns.str.strip()
df['RawSubunit'] = df['Subunit']
df = df[df['RawSubunit'].str.startswith('CSCI ', na=False)]
df = df.rename(columns={
    'Subunit': 'College', 'ID': 'Course Offering', 'Participants': 'Num Enrolled', 'Period': 'Term'
})

# 4. Filter out test/demo rows
df = df[~df['College'].str.contains(r'(?i)TEST', na=False)]
df = df[~df['Course Offering'].str.contains(r'(?i)DEMO', na=False)]

# 5. Normalize Term
df['Term'] = df['Term'].str.replace(r'^(Spring|Summer|Fall|Winter)\s+(\d{4})$', r'\1 Semester \2', regex=True)

# 6. Derive Faculty
df['Faculty'] = df['First Name'].astype(str).str.strip() + ' ' + df['Last name'].astype(str).str.strip()

# 7. Compute Num Responses and Return Percent
df['Num Responses'] = df.groupby(['Term', 'Course Offering', 'Faculty'])['Course Offering'].transform('count')
df['Return Percent'] = (df['Num Responses'] / df['Num Enrolled'] * 100).round(2).astype(str) + '%'

# 8. Department & College override
df['College'] = 'College of Science'
df['Department'] = df['RawSubunit'].str.split().str[-1].map(dept_map).fillna('')

# 9. Identify question columns
meta_cols = ['College','Department','Term','Course Offering','Course','Faculty','Num Enrolled','Num Responses','Return Percent']
non_q = {'Form of Address','Title','First Name','Last name','Program of Study','Location','Course Type',
         'Secondary instructors','Sheet','timestamp','Source of dataset','RawSubunit'}
question_cols = [c for c in df.columns if c not in meta_cols and c not in non_q]
question_cols = [c for c in question_cols if not re.search(r'\b(?:demo|test)\b', c, re.IGNORECASE)]
scale_qs = [q for q in question_cols if not q.strip().startswith('I')]
binary_qs = [q for q in question_cols if q.strip().startswith('I')]

# 10. Melt into long form
df_long = df.melt(id_vars=meta_cols, value_vars=question_cols, var_name='Question', value_name='Response')

# 🔧 Clean: Remove question number prefixes like "1. ", "10. ", etc.
df_long['Question'] = df_long['Question'].str.replace(r'^\d+\.\s*', '', regex=True)

# 🔧 FIX: Extract numeric values correctly
def extract_final_numeric(value):
    if isinstance(value, str) and ',' in value:
        parts = value.split(',')
        try:
            return float(parts[-1])
        except ValueError:
            return np.nan
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan

df_long['Numeric'] = df_long['Response'].apply(extract_final_numeric)

# 11. Classify responses
scale = df_long[df_long['Question'].isin(scale_qs) & df_long['Numeric'].notna()].copy()
binary = df_long[df_long['Question'].isin(binary_qs) & df_long['Numeric'].notna()].copy()
feedback = df_long[
    df_long['Numeric'].isna() & df_long['Response'].notna() &
    df_long['Response'].str.strip().astype(bool) &
    (df_long['Response'].str.strip() != "[IMAGE]")
].copy()

# 12. Aggregate statistics
group_vars = meta_cols + ['Question']

# For scaled numeric questions
stats_scale = (
    scale.groupby(group_vars)['Numeric']
         .agg(std=lambda x: x.std(ddof=0), median='median', mean='mean')
         .reset_index()
)
stats_scale['Std Dev, Median, Mean/ Feedback'] = stats_scale.apply(
    lambda r: f"{r['std']:.2f},{int(r['median'])},{r['mean']:.2f}", axis=1
)
stats_scale['Sum'] = ''

# For binary questions
stats_binary = binary.groupby(group_vars)['Numeric'].sum().reset_index()
stats_binary = stats_binary.rename(columns={'Numeric':'Sum'})
stats_binary['Std Dev, Median, Mean/ Feedback'] = ''

# 🛠️ For feedback comments: concatenate multiple responses
feedback_agg = (
    feedback.groupby(group_vars)['Response']
            .apply(lambda x: " | ".join(x.dropna().unique()))
            .reset_index()
)
feedback_agg['Std Dev, Median, Mean/ Feedback'] = feedback_agg['Response']
feedback_agg['Sum'] = ''

# 13. Combine all
final = pd.concat([
    stats_scale[meta_cols+['Question','Std Dev, Median, Mean/ Feedback','Sum']],
    stats_binary[meta_cols+['Question','Std Dev, Median, Mean/ Feedback','Sum']],
    feedback_agg[meta_cols+['Question','Std Dev, Median, Mean/ Feedback','Sum']]
], ignore_index=True)
final = final.sort_values(by=meta_cols+['Question'])

# 14. Write to Excel
out_path = os.path.join(output_folder, 'uwide.xlsx')
final.to_excel(out_path, index=False, engine='openpyxl')
print(f"✓ Written Excel report to {os.path.abspath(out_path)}")

# 14. Write out
# out_path = os.path.join(data_folder, 'uwide.csv')
# final.to_csv(out_path, index=False)
# print(f"✓ Written report to {out_path}")