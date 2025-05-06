import pandas as pd

# === Load files ===
coschem_df = pd.read_excel("transformation/coschem.xlsx")
uwide_df = pd.read_excel("transformation/uwide.xlsx")
course_offerings_df = pd.read_csv("sample-files/FA22-SU24 course offerings_complete.csv")

# === Parse course offering IDs ===
def parse_course_offering_id(offering_id):
    parts = offering_id.split('_')
    if len(parts) >= 6:
        course_id = '_'.join(parts[:4])  # e.g., CHEM_100_01_1
        crn = parts[4]                   # e.g., 1491
        term = parts[5]                  # e.g., 2229
        return pd.Series([course_id, crn, term])
    return pd.Series([None, None, None])

course_offerings_df[['Course ID', 'CRN', 'Term']] = course_offerings_df['Course Offering ID'].apply(parse_course_offering_id)

# === Prepare merge keys for relaxed match ===
def split_course_offering(value):
    parts = value.split('_')
    if len(parts) == 5:
        term = parts[0]
        subj = parts[1]
        course = parts[2]
        section = parts[3]
        suffix = parts[4]
        # Rearranged to match registrar format
        course_id = f"{subj}_{course}_{suffix}_{section}"
        return pd.Series([term, course_id])
    return pd.Series([None, None])


coschem_df[['TermCode', 'ParsedCourseID']] = coschem_df['Course Offering'].apply(split_course_offering)
uwide_df[['TermCode', 'ParsedCourseID']] = uwide_df['Course Offering'].apply(split_course_offering)

course_offerings_df['ParsedCourseID'] = course_offerings_df['Course ID']
course_offerings_df['TermCode'] = course_offerings_df['Term']

def simplify_course_id(parsed_id):
    if isinstance(parsed_id, str):
        parts = parsed_id.split('_')
        if len(parts) >= 2:
            return '_'.join(parts[:2])  # e.g., CHEM_100
    return None

coschem_df['SimplifiedCourseID'] = coschem_df['ParsedCourseID'].apply(simplify_course_id)
uwide_df['SimplifiedCourseID'] = uwide_df['ParsedCourseID'].apply(simplify_course_id)
course_offerings_df['SimplifiedCourseID'] = course_offerings_df['ParsedCourseID'].apply(simplify_course_id)

# Merge with strict keys
coschem_merged = pd.merge(
    coschem_df,
    course_offerings_df[['ParsedCourseID', 'TermCode', 'CRN']],
    on=['ParsedCourseID', 'TermCode'],
    how='left'
)

uwide_merged = pd.merge(
    uwide_df,
    course_offerings_df[['ParsedCourseID', 'TermCode', 'CRN']],
    on=['ParsedCourseID', 'TermCode'],
    how='left'
)

# === Build final Course Offering ===
def build_corrected_course_offering(row):
    if pd.notnull(row['CRN']) and pd.notnull(row['ParsedCourseID']) and pd.notnull(row['TermCode']):
        parts = row['ParsedCourseID'].split('_')
        if len(parts) >= 4:
            return f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}_{int(row['CRN'])}_{row['TermCode']}"
    return row['Course Offering']

coschem_merged['Course Offering'] = coschem_merged.apply(build_corrected_course_offering, axis=1)
uwide_merged['Course Offering'] = uwide_merged.apply(build_corrected_course_offering, axis=1)

# === Clean output ===
columns_to_drop = ['ParsedCourseID', 'SimplifiedCourseID', 'TermCode', 'CRN']
coschem_final = coschem_merged.drop(columns=columns_to_drop, errors='ignore')
uwide_final = uwide_merged.drop(columns=columns_to_drop, errors='ignore')

# === Save ===
coschem_final.to_excel("coschem-final.xlsx", index=False)
uwide_final.to_excel("uwide-final.xlsx", index=False)
