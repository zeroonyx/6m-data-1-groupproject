import streamlit as st

# section 1

# Sets the page configuration
# You can set the page title and layout here
st.set_page_config(page_title="SG Job Coach | Career Intelligence", layout="wide")


# Marketing Header
st.title("SG Job Coach")
st.markdown("#### *Master the Singapore Job Market with Strategic Career Intelligence*")
st.caption("Analyzing over 1 million data points to give you a competitive edge.")

st.header("Strategic Career Intelligence")
# st.subheader("What this app will show")
# st.markdown("""
# 1. **When to Apply?** 
#     * Which days of the week and months of the year do job postings receive the most views and applications?
# 2. **Title Optimization?**
#     * Do certain keywords in job titles (e.g. Senior, Junior, Lead) correlate with higher views and application counts?        
# 3. **Low-Competition Niches?**
#     * Which primary job categories have the lowest applications-per-vacancy ratio, indicating less competition?
# """)
intro_col1, intro_col2, intro_col3 = st.columns(3)

# We use &w=800&h=500&fit=crop to force a consistent 8:5 aspect ratio
img_size = "&w=800&h=500&fit=crop"

with intro_col1:
    st.subheader("Perfect Your Timing")
    st.image("https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format" + img_size, 
             use_container_width=True)
    st.markdown("""
    **Beat the Crowd**
    * **The Insight:** Identify exactly when recruiters are most active.
    * **Your Edge:** Apply during high-visibility windows (Day & Month) to ensure your profile stays at the top of the pile.
    """)

with intro_col2:
    st.subheader("Position Like a Pro")
    st.image("https://images.unsplash.com/photo-1653038417332-6db0ff9d4bfb?auto=format" + img_size, 
             use_container_width=True)
    st.markdown("""
    **Optimize Your Title**
    * **The Insight:** We analyze how keywords like **'Senior'** vs. **'Lead'** change engagement levels.
    * **Your Edge:** Adjust your search and resume keywords to align with the market’s highest-performing roles.
    """)

with intro_col3:
    st.subheader("Find Blue Oceans")
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format" + img_size, 
             use_container_width=True)
    st.markdown("""
    **Minimize Competition**
    * **The Insight:** Spot high-vacancy categories with surprisingly low applicant volumes.
    * **Your Edge:** Secure higher salary offers by targeting high-demand, low-competition niches.
    """)

st.divider()

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
    df["metadata_newPostingDate"] = pd.to_datetime(df["metadata_newPostingDate"])
    # Mapping for readability
    days_map = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
    months_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                  7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    
    # Create temporal columns
    df['day_name'] = df['metadata_newPostingDate'].dt.dayofweek.map(days_map)
    df['month_name'] = df['metadata_newPostingDate'].dt.month.map(months_map)
    
    # Force chronological sorting
    day_order = list(days_map.values())
    month_order = list(months_map.values())
    df['day_name'] = pd.Categorical(df['day_name'], categories=day_order, ordered=True)
    df['month_name'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)

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
# st.markdown(f"## :red[{len(filtered_df):,}] Matching Job Postings")

st.markdown(
    f"""
    <div style="line-height: 1; margin-bottom: 10px;">
        <span style="font-size: 56px; font-weight: 700; color: #FF4B4B;">
            {len(filtered_df):,}
        </span>
        <span style="font-size: 32px; font-weight: 600; color: #31333F;">
            Matching Data Points
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- Key Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Job Market Volume", f"{len(filtered_df):,}")
col2.metric("Average Pay", f"${filtered_df['average_salary'].mean():,.0f}")
col3.metric("Median Benchmark", f"${filtered_df['average_salary'].median():,.0f}")
# Corrected col4 logic (removed 'sqm' typo)
col4.metric("Min Average Pay", f"${filtered_df['average_salary'].min():,.0f}")

st.divider()



# visualization 
import plotly.express as px


st.header("Perfect Your Timing")
st.markdown("Discover exactly when the market moves. We compare **Demand** (Views/Apps) vs **Supply** (New Postings).")

# --- DATA PREP FOR DASHBOARD ---
# 1. Weekly Stats
day_stats = filtered_df.groupby('day_name', observed=True).agg({
    'metadata_totalNumberOfView': 'sum',
    'metadata_totalNumberJobApplication': 'sum',
    'title': 'count' # This is the "New Postings"
}).reset_index().rename(columns={'title': 'Postings', 'metadata_totalNumberOfView': 'Views', 'metadata_totalNumberJobApplication': 'Apps'})

# 2. Calculate Efficiency
day_stats['Conv %'] = (day_stats['Apps'] / day_stats['Views'] * 100).round(2)

# --- VISUALIZATION ROW 1: Weekly Volume ---
tab1, tab2 = st.tabs(["🕒 Weekly Trends", "📆 Monthly Trends"])

with tab1:
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.subheader("Weekly Market Volume")
        st.caption("""
            **Market Pulse:** Comparing total interest (Views) against action (Apps). 
            Watch for days where the 'Gap' closes—it signals a surge in active competitors.
        """)
        # Dual axis equivalent in Plotly: Create a combined bar/line chart
        fig_day = px.bar(day_stats, x='day_name', y='Apps', color_discrete_sequence=['#3399ff'], 
                         title="Total Applications by Day")
        fig_day.add_scatter(x=day_stats['day_name'], y=day_stats['Views'], name='Views', 
                            yaxis='y2', line=dict(color='#ff4d4d', width=3))
        fig_day.update_layout(yaxis2=dict(overlaying='y', side='right'), showlegend=False)
        st.plotly_chart(fig_day, use_container_width=True)

    with col_b:
        st.subheader("🏗️ Weekly Supply")
        st.caption("""
            **The Early Bird Advantage:** This tracks when companies drop new roles. 
            Applying on high-supply days ensures your resume is at the top of the pile 
            before the 'Market Volume' (left chart) catches up.
        """)
        # New Postings Chart (Teal Theme)
        fig_day_supply = px.bar(day_stats, x='day_name', y='Postings', 
                                color_discrete_sequence=['#008080'],
                                title="New Job Postings by Day")
        st.plotly_chart(fig_day_supply, use_container_width=True)


    with col_c:
        st.subheader("Conversion Efficiency (%)")
        st.caption("""
            **The Decisiveness Score:** This measures the 'App-to-View' ratio. 
            A higher percentage means users are moving from browsing to applying—identify 
            these peaks to time your most important applications.
        """)
        
        fig_conv = px.line(day_stats, x='day_name', y='Conv %', markers=True,
                           color_discrete_sequence=['#9b59b6'], title="App-to-View Ratio")
        
        # This adds the '%' suffix to the Y-axis and hover labels
        fig_conv.update_layout(
            yaxis=dict(
                ticksuffix="%",
                range=[0, day_stats['Conv %'].max() * 1.2] # Adds a little headroom
            ),
            xaxis_title="Day of Week",
            yaxis_title="Efficiency (%)"
        )
        
        st.plotly_chart(fig_conv, use_container_width=True)

with tab2:
    # 1. Monthly Aggregation
    month_stats = filtered_df.groupby('month_name', observed=True).agg({
        'metadata_totalNumberOfView': 'sum',
        'metadata_totalNumberJobApplication': 'sum',
        'title': 'count'
    }).reset_index().rename(columns={
        'title': 'Postings', 
        'metadata_totalNumberOfView': 'Views', 
        'metadata_totalNumberJobApplication': 'Apps'
    })

    # 2. Calculate Efficiency
    month_stats['Conv %'] = (month_stats['Apps'] / month_stats['Views'] * 100).round(2)

    col_d, col_e, col_f = st.columns(3)
    
    with col_d:
        st.subheader("Monthly Market Volume")
        st.caption("""
            **Seasonality Radar:** Spot the big hiring waves. In Singapore, peaks often 
            align with the 'Post-CNY' shuffle or the mid-year 'Q3 Budget' approvals.
        """)
        # Dual axis Bar + Line
        fig_month = px.bar(month_stats, x='month_name', y='Apps', 
                           color_discrete_sequence=['#3399ff'], 
                           title="Monthly Application Volume")
        
        fig_month.add_scatter(x=month_stats['month_name'], y=month_stats['Views'], 
                              name='Views', yaxis='y2', 
                              line=dict(color='#ff4d4d', width=3))
        
        # fig_month.update_layout(
        #     yaxis2=dict(overlaying='y', side='right'),
        #     showlegend=False,
        #     xaxis_title="Month",
        #     yaxis_title="Total Applications"
        # )

        fig_month.update_layout(
            xaxis_title="Month",
            # Primary Axis (Left)
            yaxis=dict(
                title=dict(
                    text="Total Applications",
                    font=dict(color="#3399ff") # Nesting font inside title
                ),
                tickfont=dict(color="#3399ff"),
                tickformat=".2s" # Forces 'k' format (e.g., 5.0k)
            ),
            # Secondary Axis (Right)
            yaxis2=dict(
                title=dict(
                    text="Total Views",
                    font=dict(color="#ff4d4d") # Nesting font inside title
                ),
                tickfont=dict(color="#ff4d4d"),
                tickformat=".2s", # Forces 'k' format (e.g., 5.0k)
                overlaying='y',
                side='right',
                anchor="x",
                showgrid=False
            ),
            showlegend=False,
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig_month, use_container_width=True)

    with col_e:
        st.subheader("📦 Monthly Supply")
        st.caption("""
            **Inventory Forecast:** High supply months represent a 'Buyer's Market' for talent. 
            More choices mean you can be pickier with your applications and expect more 
            active outreach from recruiters.
        """)
        # New Postings Chart (Teal Theme)
        fig_month_supply = px.bar(month_stats, x='month_name', y='Postings', 
                                  color_discrete_sequence=['#008080'],
                                  title="New Job Postings by Month")
        st.plotly_chart(fig_month_supply, use_container_width=True)


    with col_f:
        st.subheader("Seasonal Efficiency (%)")
        st.caption("""
            **The Commitment Metric:** This ratio filters out 'curiosity' clicks. 
            A peak here reveals the months when candidates are most serious about moving—perfect 
            for benchmarking your own career search intensity.
        """)
        
        fig_month_conv = px.line(month_stats, x='month_name', y='Conv %', markers=True,
                                 color_discrete_sequence=['#f39c12'], 
                                 title="Monthly App-to-View Ratio")
        
        # Apply the % suffix and clean up the layout
        fig_month_conv.update_layout(
            yaxis=dict(
                ticksuffix="%",
                range=[0, month_stats['Conv %'].max() * 1.2], # Headroom for the peak
                showgrid=True
            ),
            xaxis_title="Month",
            yaxis_title="Efficiency (%)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig_month_conv, use_container_width=True)

    # Marketing Insight for Tab 2
    peak_month = month_stats.loc[month_stats['Conv %'].idxmax(), 'month_name']
    st.info(f"💡 **Market Intelligence:** Historical data shows that **{peak_month}** is the most 'decisive' month for your current filters. Plan your big career moves around this window!")


# --- INSIGHTS BOX ---
best_day = day_stats.loc[day_stats['Conv %'].idxmax(), 'day_name']
st.success(f"**Pro Tip:** Based on current filters, **{best_day}** shows the highest Conversion Efficiency. This is your 'Golden Window' to apply.")




# --- Visualization Layout ---
st.header("📊 Market Deep-Dive")
col_left, col_right = st.columns(2)


# Left Column: Existing Position Level Chart
with col_left:
    st.subheader("Salary Hierarchy")
    avg_price_by_positionlevel = (
        filtered_df.groupby("positionLevels", as_index=False)["average_salary"]
        .mean()
        .sort_values("average_salary", ascending=False)
    )

    fig_job = px.bar(
        avg_price_by_positionlevel, 
        x="positionLevels",
        y="average_salary",
        labels={"average_salary": "Avg Salary ($)", "positionLevels": "Level"},
        color="average_salary",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_job, use_container_width=True)

# Right Column: New Primary Category Chart
with col_right:
    st.subheader("Salary Performance per Category")
    
    # 1. Group by Primary Category and calculate stats
    salary_stats = filtered_df.groupby('primary_category').agg(
        Avg_Salary=('average_salary', 'mean'),
        Job_Count=('primary_category', 'count')
    ).reset_index()

    # 2. Filter for categories with at least 50 postings and sort
    salary_summary = (
        salary_stats[salary_stats['Job_Count'] > 50]
        .sort_values('Avg_Salary', ascending=True) # Ascending True for a nice horizontal rank
    )

    if not salary_summary.empty:
        fig_cat = px.bar(
            salary_summary,
            x='Avg_Salary',
            y='primary_category',
            orientation='h', # Horizontal bar for readability
            title="Top Paying Categories (Min. 50 Postings)",
            labels={"Avg_Salary": "Average Salary ($)", "primary_category": "Category"},
            text_auto='.2s' # Automatically adds formatted labels to bars
        )
        
        # Update layout to make it look cleaner
        fig_cat.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("Not enough data in this range to show Category stats (needs >50 postings).")

# skip Tells Streamlit to put the following content in the right column

st.divider() # Visual break at the bottom of the page

with st.expander("📝 Data Methodology & Disclaimer"):
    st.markdown("""
    **Data Source:** This analysis utilizes a dataset of over 1 million historical job postings in Singapore.
    
    **Methodology:**
    * Salary figures are calculated as the mean of the provided `salary_minimum` and `salary_maximum`.
    * Categories and Position Levels are based on standardized employer inputs at the time of posting.
    
    **Disclaimer:** *SG Job Coach* provides market trends for strategic guidance only. We do not guarantee the availability or salary of any specific role. All data is subject to "point-in-time" limitations and may not reflect real-time market shifts. 
    """)

from datetime import datetime
print(f"🟢 Rerun at: {datetime.now()}")
