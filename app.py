import streamlit as st

# section 1

# Sets the page configuration
# You can set the page title and layout here
st.set_page_config(page_title="SG Job Coach Analysis", layout="wide")

st.title("SG Job Coach Analysis")
st.caption("An insightful dashboard looking into Singapore job market trends.")

st.header("Dashboard Overview")
st.subheader("What this app will show")
st.markdown("""
1. **When to Apply?** 
    * Which days of the week and months of the year do job postings receive the most views and applications?
2. **Title Optimization?**
    * Do certain keywords in job titles (e.g. Senior, Junior, Lead) correlate with higher views and application counts?        
3. **Low-Competition Niches?**
    * Which primary job categories have the lowest applications-per-vacancy ratio, indicating less competition?
""")


# Section 2
#load data
import pandas as pd

DATA_PATH = "./data/SGJobData_cleaned.csv"


# Lesson assumption:
# this dataset has already gone through EDA and basic cleaning.
# Here we focus on dashboard building, not data cleaning.
# We still set the datetime dtype explicitly for reliable filtering and charting.
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["year_month"] = pd.to_datetime(df["year_month"])
    return df

df = load_data(DATA_PATH)




# big data requires filter

# add sidebar with filters
st.sidebar.header("Filters")

choices_day_of_week = sorted(df["day_of_week"].dropna().unique())
choices_month_of_year = sorted(df["month_of_year"].dropna().unique())
choices_title = sorted(df["title"].dropna().unique())
choices_positionLevels = sorted(df["positionLevels"].dropna().unique())

selected_positionLevels = st.sidebar.multiselect("Position Level", choices_positionLevels, default=['Professional'])

# Salary filter
min_price = int(df["average_salary"].min())
max_price = int(df["average_salary"].max())

price_range = st.sidebar.slider(
    "Average Salary Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=500,
)


# Raw Rows is big all loaded: 1,024,366 | Columns: 7
# apply filter 
filtered_df = df.copy()

if selected_positionLevels:
    filtered_df = filtered_df[filtered_df["positionLevels"].isin(selected_positionLevels)]

filtered_df = filtered_df[
    filtered_df["average_salary"].between(price_range[0], price_range[1])
]

# display data with filter 

st.header("Filtered Results")
st.write(f"Matching rows: {len(filtered_df):,} | Columns: {len(filtered_df.columns)}")
st.dataframe(filtered_df.head(20), width="stretch")

st.header("Key Metrics")

# Create four columns for the metrics and unpack them
# We can then use each column to place a metric
col1, col2, col3, col4 = st.columns(4)

# Populate each column with a metric by passing label and value
col1.metric("Job Posting", f"{len(filtered_df):,}")
col2.metric("Average Salary", f"${filtered_df['average_salary'].mean():,.0f}")
col3.metric("Median Average Salary", f"${filtered_df['average_salary'].median():,.0f}")
col4.metric("Min Average Salary", f"{filtered_df['average_salary'].median():.1f} sqm")


# visualization 
import plotly.express as px

st.header("Visual Analysis")

col_left, col_right = st.columns(2)

# Tells Streamlit to put the following content in the left column
with col_left:
    st.subheader("average_salary Price by Position level")
    avg_price_by_positionlevel = (
        filtered_df.groupby("positionLevels", as_index=False)["average_salary"]
        .mean()
        .sort_values("average_salary", ascending=False)
        .head(10) # Top 10 towns only for clarity
    )

    fig_job = px.bar(
        avg_price_by_positionlevel, 
        x="positionLevels",    # Changed from "town"
        y="average_salary",    # Changed from "resale_price"
        title="Average Salary by Position Level"
    )
    st.plotly_chart(fig_job, width="stretch")

# skip Tells Streamlit to put the following content in the right column




from datetime import datetime
print(f"🟢 Rerun at: {datetime.now()}")
