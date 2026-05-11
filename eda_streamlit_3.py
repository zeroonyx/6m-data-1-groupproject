import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 0. Professional Theme Configuration ---
PRIMARY_BLUE = "#1e3a8a"      # Navy Blue (Demand/Views)
SECONDARY_RED = "#b91c1c"     # Deep Red (Competition/Apps)
NEUTRAL_SLATE = "#64748b"     
TEMPLATE = "plotly_white"
SEQUENTIAL_SCALE = "Blues"

# Load data
df = pd.read_csv("../data/SGJobData_Persona4.csv")

# Extract Year from originalPosting_Month (Format: YYYY-MM)
df['year'] = pd.to_datetime(df['originalPosting_Month']).dt.year.astype(str)

st.set_page_config(page_title="SG Job Insights", layout="wide")


# --- GLOBAL FILTERS (Sidebar) ---
st.sidebar.header("Global Filters")
available_years = sorted(df['year'].unique().tolist())
selected_years = st.sidebar.multiselect("Select Posting Year(s)", 
                                        options=available_years, 
                                        default=available_years)

# Apply Year Filter to the entire dataframe
df = df[df['year'].isin(selected_years)]

st.title(f"Singapore Job Market Insights (Year-on-Year) [ {', '.join(selected_years)}]")
# --- 1. Timing Chart ---
st.subheader(f"1. Timing: When is the Market Most Active?{selected_years}")
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['Time_Label'] = df['originalPosting_Day'] + "\n" + df['originalPosting_Month'].astype(str)

temporal_day = df[df['metadata_totalNumberJobApplication'] >0].groupby(['originalPosting_Day']).agg({
    'metadata_totalNumberOfView': 'mean',
    'metadata_totalNumberJobApplication': 'mean'
}).reindex(day_order).reset_index()



# 3. Aggregate for the chart
# temporal_day = df.groupby(['Time_Label', 'category'])['metadata_totalNumberJobApplication'].sum().reset_index()

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=temporal_day['originalPosting_Day'], 
    y=temporal_day['metadata_totalNumberOfView'], 
    name='Avg Views', 
    marker_color=PRIMARY_BLUE,
    opacity=0.8
))
fig1.add_trace(go.Scatter(
    x=temporal_day['originalPosting_Day'], 
    y=temporal_day['metadata_totalNumberJobApplication'], 
    name='Avg Apps', 
    yaxis='y2', 
    line=dict(color=SECONDARY_RED, width=3)
))

fig1.update_layout(
    template=TEMPLATE,
    yaxis=dict(title=dict(text='Average Views', font=dict(color=PRIMARY_BLUE))),
    yaxis2=dict(
        title=dict(text='Average Applications', font=dict(color=SECONDARY_RED)),
        overlaying='y', 
        side='right'
    ),
    legend=dict(x=0, y=1.1, orientation='h'),
    margin=dict(t=50, b=50)
)
st.plotly_chart(fig1, use_container_width=True)

# --- 2. Market Density (Treemap) ---
def get_level(title):
    t = str(title).lower()
    if any(word in t for word in ['senior', 'sr', 'snr']): return 'Senior'
    if any(word in t for word in ['junior', 'jr', 'entry']): return 'Junior'
    if any(word in t for word in ['lead', 'head', 'manager', 'director', 'vp']): return 'Lead/Manager'
    return 'General'

df['level_tag'] = df['positionLevels'].apply(get_level)
top_cats = df['category'].value_counts().nlargest(10).index
df_filtered = df[df['category'].isin(top_cats)].copy()

hierarchical_data = df_filtered.groupby(['category', 'level_tag', 'salary_range'], observed=False).agg({
    'metadata_totalNumberJobApplication': 'mean',
    'numberOfVacancies': 'sum'
}).reset_index()

st.subheader(f"2.Market Concentration View : [{', '.join(selected_years)}")

fig2 = px.treemap(
    hierarchical_data,
    path=[px.Constant("Market Overview"), 'category', 'level_tag', 'salary_range'],
    values='numberOfVacancies',
    color='metadata_totalNumberJobApplication',
    color_continuous_scale=SEQUENTIAL_SCALE,
    labels={'metadata_totalNumberJobApplication': 'Total Job Applications'},
    title=f"Market Concentration for Selected Years: [{', '.join(selected_years)}]"
)
st.plotly_chart(fig2, use_container_width=True)

# --- 3. The 'Sweet Spot' Quadrant ---
cat_stats = df.groupby('category').agg({
    'metadata_totalNumberJobApplication': 'sum',
    'numberOfVacancies': 'sum',
    'average_salary': 'mean'
}).reset_index()

cat_stats['apps_per_vacancy'] = cat_stats['metadata_totalNumberJobApplication'] / cat_stats['numberOfVacancies']
avg_salary = cat_stats['average_salary'].median()
avg_comp = cat_stats['apps_per_vacancy'].median()

st.subheader(f"3. The 'Sweet Spot': Salary vs Competition : {', '.join(selected_years)}")
fig3 = px.scatter(
    cat_stats, 
    x='apps_per_vacancy', 
    y='average_salary',
    size='numberOfVacancies',
    color='average_salary',
    color_continuous_scale="RdBu_r",
    hover_name='category',
    labels={'average_salary': 'Average Salary','numberOfVacancies':'Total Vacancies','apps_per_vacancy':'Apps Per Vacancy'}
)
fig3.add_hline(y=avg_salary, line_dash="dash", line_color=NEUTRAL_SLATE)
fig3.add_vline(x=avg_comp, line_dash="dash", line_color=NEUTRAL_SLATE)
st.plotly_chart(fig3, use_container_width=True)

# --- 4. Industry Deep-Dive ---
salary_order = ['0-3k', '3k-6k', '6k-9k', '9k-12k', '12k+']
df['salary_range'] = pd.Categorical(df['salary_range'], categories=salary_order, ordered=True)

st.sidebar.markdown("---")
st.sidebar.header("Filter: Industry Deep-Dive")
selected_cat = st.sidebar.selectbox("Select Category", ["All Industries"] + sorted(df['category'].unique().tolist()))

filtered_df = df.copy()
if selected_cat != "All Industries":
    filtered_df = filtered_df[filtered_df['category'] == selected_cat]

plot_data = filtered_df.groupby('salary_range', observed=False).agg({
    'numberOfVacancies': 'sum',
    'metadata_totalNumberJobApplication': 'mean'
}).reset_index()

st.subheader(f"4. Demand vs. Competition: {selected_cat} [ {', '.join(selected_years)}]")
fig4 = go.Figure()
fig4.add_trace(go.Bar(x=plot_data['salary_range'], y=plot_data['numberOfVacancies'], name='Total Vacancies', marker_color=PRIMARY_BLUE))
fig4.add_trace(go.Scatter(x=plot_data['salary_range'], y=plot_data['metadata_totalNumberJobApplication'], name='Avg Apps', line=dict(color=SECONDARY_RED, width=3), yaxis='y2'))
fig4.update_layout(template=TEMPLATE, yaxis2=dict(overlaying='y', side='right'))
st.plotly_chart(fig4, use_container_width=True)

# --- 5. Skill Set Analysis ---
st.subheader( f"5. Required Skill Sets (Top 10) [ {', '.join(selected_years)}]")
skills = ['SQL','API','Database','Data Engineer','AI','Java', 'Python', 'Accounting', 'Digital Marketing', 'Engineering', 'Project Management', 'Data','AWS','Azure','Google Cloud','Artificial Intelligence','Machine Learning','Cloud','Cybersecurity','DevOps','UX','UI','Mobile','Frontend','Backend','Full Stack']
skill_counts = {skill: df['title'].str.contains(f' {skill} ', case=False).sum() for skill in skills}
skill_df = pd.DataFrame(list(skill_counts.items()), columns=['Skill', 'Demand']).sort_values('Demand', ascending=False).head(10)

fig5 = px.pie(skill_df, values='Demand', names='Skill', title="Top Skills in Demand")
st.plotly_chart(fig5, use_container_width=True)


# --- 6. IT Industry Vacancy Comparison (Year-on-Year) ---
st.subheader(f"6. {selected_cat}: Year-on-Year Vacancy Comparison [{', '.join(selected_years)}]")

# 1. Filter for IT Category
if selected_cat != "All Industries":
    # it_df = df[df['category'] == 'Information Technology'].copy()
    it_df = df[df['category'] == selected_cat].copy()
else : 
    it_df = df[df['category'] == 'Information Technology'].copy()


# 2. Ensure correct order for salary ranges
salary_order = ['0-3k', '3k-6k', '6k-9k', '9k-12k', '12k+']
it_df['salary_range'] = pd.Categorical(it_df['salary_range'], categories=salary_order, ordered=True)

# 3. Aggregate Vacancies by Year and Salary Range
it_yoy_data = it_df.groupby(['year', 'salary_range'], observed=False)['numberOfVacancies'].sum().reset_index()

# 4. Create Grouped Bar Chart
# Note: Using PRIMARY_BLUE for 2023 and SECONDARY_RED for 2024 automatically 
# via the color_discrete_sequence based on your defined constants.
if selected_cat != "All Industries": str_title = selected_cat
else:
    str_title = "IT"

fig_it_yoy = px.bar(
    it_yoy_data, 
    x='salary_range', 
    y='numberOfVacancies', 
    color='year', 
    barmode='group',
    color_discrete_sequence=[PRIMARY_BLUE, SECONDARY_RED, "#94a3b8"], # Navy, Red, and Slate for a 3rd year if any
    title=f"{str_title} Vacancies by Salary Range (Yearly Comparison)",
    labels={
        'numberOfVacancies': 'Total Vacancies', 
        'salary_range': 'Salary Range',
        'year': 'Year'
    }
)

# 5. Apply Theme and Layout
fig_it_yoy.update_layout(
    template=TEMPLATE,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=80)
)

st.plotly_chart(fig_it_yoy, use_container_width=True)



# ZERO APPLICATION PER CATEGORY

st.subheader(f" 7. Year-on-Year Gap: Zero Applications by Category {selected_cat}: [{', '.join(selected_years)}]")
df['year'] = pd.to_datetime(df['originalPosting_Month']).dt.year.astype(str)

def extract_skills(title):
    # Returns a list of skills found in the string
     for skill in skills :
         if ' '+skill.lower()+' ' in str(title).lower():
              return skill

df['skills_found'] = df['title'].apply(extract_skills)
df['skills_found'].value_counts(ascending=False)

filtered_df = df[
    (df['year'].isin(selected_years)) & 
    (df['category'] == selected_cat)
]
# 1. Calculate the zero-rate grouped by both Year and Category
zero_apps_yearly = filtered_df.groupby(['year', 'category','skills_found']).agg(
    total_jobs=('metadata_totalNumberJobApplication', 'count'),
    zero_app_jobs=('metadata_totalNumberJobApplication', lambda x: (x == 0).sum())
).reset_index()

zero_apps_yearly['zero_rate_percent'] = (zero_apps_yearly['zero_app_jobs'] / zero_apps_yearly['total_jobs']) * 100

# 2. Create a grouped bar chart
fig_zeros_yearly = px.bar(
    zero_apps_yearly,
    x='skills_found',
    y='zero_rate_percent',
    color='year',
    barmode='group', # Puts 2023 and 2024 bars side-by-side
    title="Comparison: % of Jobs with 0 Applications",
    labels={
        'zero_rate_percent': '% of Jobs with 0 Apps', 
        'category': 'Job Category', 
        'originalPosting_Month': 'Year'
    },
    color_discrete_sequence=px.colors.qualitative.Safe,
    text_auto='.1f' # Displays the percentage on top of the bars
)

# 3. Clean up the UI
fig_zeros_yearly.update_layout(
    xaxis_tickangle=-45,
    legend_title_text='Year',
    hovermode="x unified"
)

st.plotly_chart(fig_zeros_yearly, use_container_width=True)