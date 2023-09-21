import streamlit as st
import sqlfluff as sf
import pandas as pd

st.set_page_config(page_title="Online SQL Formatter", page_icon="🎓", layout="wide")
st.title("🎓 Online SQL Formatter")

# Sidebar
dialects = list(d.name for d in sf.list_dialects())
st.sidebar.subheader("Settings")
selected_dialect = st.sidebar.selectbox('Select your dialect', dialects, index=2)
comma_style = st.sidebar.radio('Comma style', ['trailing', 'leading'], index=1)
join_style = st.sidebar.radio('Join style', ['indented', 'no indent'], index=0)
if join_style == 'indented':
    join_style = True
else:
    join_style = False

# Main page
input_sql = st.text_area("Enter your SQL query here", height=400, key="sql")
input_sql_with_config = f"-- sqlfluff:layout:type:comma:line_position:{comma_style}\n-- sqlfluff:rules:capitalisation.keywords:capitalisation_policy:upper\n-- sqlfluff:indentation:indented_joins:{join_style}\n-- sqlfluff:exclude_rules:LT12\n{input_sql}"
lint = sf.lint(input_sql_with_config, dialect=selected_dialect, config_path=".sqlfluff")
params = input_sql_with_config.count("-- sqlfluff:")
issues = []
for record in lint:
    pos = str(record.get("line_no")-params) + ' / ' + str(record.get("line_pos"))
    rule = record.get("code")
    description = record.get("description")
    issue = {"Line / Position": pos, "Rule": rule, "Description": description}
    issues.append(issue)
output_sql = sf.fix(input_sql_with_config, dialect=selected_dialect, config_path=".sqlfluff")
output_sql_without_config_list = []
for row in output_sql.split("\n"):
    if row == "":
        continue
    if row.startswith("--"):
        continue
    output_sql_without_config_list.append(row+"\n")
output_sql_without_config = "".join(output_sql_without_config_list)
st.subheader("Formatted SQL")
st.code(output_sql_without_config, language="sql", line_numbers=True)

# Issues
with st.expander("Expand issues"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your SQL")
        st.code(input_sql, language="sql", line_numbers=True)
    with col2:
        st.subheader("Issues with original SQL")
        st.dataframe(issues)
