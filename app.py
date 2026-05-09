import streamlit as st

# --- 1. CONFIGURATION & CSS (Add at the very top, after imports) ---
GRAY_BAR = '#999999'    
RED_ACCENT = '#C85050'  
CHART_HEIGHT = 380      

st.markdown("""
    <style>
    /* Pulls Pro Tip closer to charts */
    .element-container:has(iframe) { margin-bottom: -35px !important; }
    
    /* Pulls Expander closer to Pro Tip */
    div[data-testid="stExpander"] { margin-top: -15px !important; }
    
    /* Clean up the Expander appearance */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        color: #666666 !important;
    }
    .streamlit-expanderContent {
        background-color: #f9f9f9 !important;
        border-left: 3px solid #999999 !important;
    }
    </style>
    """, unsafe_allow_html=True)


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
@st.cache_data
def get_seniority_base_data(df):
    """
    Processes 1M+ rows of text once and caches it.
    This avoids running regex and explode on every slider movement.
    """
    target_keywords = [
        'senior', 'junior', 'lead', 'manager', 'director', 
        'intern', 'associate', 'head', 'principal', 'staff',
        'analyst', 'specialist', 'coordinator', 'executive'
    ]
    
    # Pre-calculate the word-level table
    df_words = df[['title', 'metadata_totalNumberOfView', 'metadata_totalNumberJobApplication', 'positionLevels', 'average_salary']].copy()
    df_words['word'] = df_words['title'].str.lower().str.replace(r'[^a-zA-Z\s]', ' ', regex=True).str.split()
    df_words = df_words.explode('word')
    
    # Only keep the keywords we care about for the bubble chart
    return df_words[df_words['word'].isin(target_keywords)]

df = load_data(DATA_PATH)
# Call this once after loading your main df
df_seniority_all = get_seniority_base_data(df)

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

# Sidebar Logic for the Bubble Chart Volume
# We calculate the slider range based on the global seniority data
st.sidebar.divider()
st.sidebar.header("Visual Filters (Bubble Chart)")

# Quick aggregation for slider bounds
vol_stats = df_seniority_all['word'].value_counts()
q_min = int(vol_stats.quantile(0.01))
q_max = int(vol_stats.quantile(0.99))

min_vol, max_vol = st.sidebar.slider(
    "Filter by Job Volume",
    min_value=q_min,
    max_value=q_max,
    value=(q_min, q_max),
    step=2000
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


# --- VISUALIZATION ROW 1: Weekly Volume v 2 start---
# --- CONFIGURATION ---
GRAY_BAR = '#999999'    
RED_ACCENT = '#C85050'  
CHART_HEIGHT = 380      

tab3, tab4 = st.tabs(["🕒 Weekly Trends", "📆 Monthly Trends"])

with tab3:
    # 1. Logic to find the "Sweet Spot" dynamically
    # Find the absolute peak supply day (e.g., Tue)
    peak_supply_val = day_stats['Postings'].max()
    peak_supply_day = day_stats.loc[day_stats['Postings'].idxmax(), 'day_name']
    
    # Filter for days that have high supply (within 20% of the peak)
    high_supply_days = day_stats[day_stats['Postings'] >= (peak_supply_val * 0.8)]
    
    # Of those high supply days, find the one with the lowest competition (Apps)
    sweet_spot_row = high_supply_days.loc[high_supply_days['Apps'].idxmin()]
    sweet_spot_day = sweet_spot_row['day_name']
    
    # Calculate how much lower the competition is compared to the peak app day
    peak_apps = day_stats['Apps'].max()
    comp_reduction = round(((peak_apps - sweet_spot_row['Apps']) / peak_apps) * 100)


    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.subheader("Weekly App Volume")
        st.caption("""
            **Market Pulse:** Comparing total interest (Views) against action (Apps). 
            Watch for days where the 'Gap' closes—it signals a surge in active competitors.
        """)
        fig_day = px.bar(day_stats, x='day_name', y='Apps', color_discrete_sequence=[GRAY_BAR], opacity=0.8)
        fig_day.add_scatter(x=day_stats['day_name'], y=day_stats['Views'], name='Views', 
                            yaxis='y2', line=dict(color=RED_ACCENT, width=3))
        
        fig_day.update_layout(
            height=CHART_HEIGHT, margin=dict(l=10, r=10, t=30, b=0),
            showlegend=False, xaxis_title="", 
            yaxis=dict(title=dict(text="Apps", font=dict(color=GRAY_BAR)), tickfont=dict(color=GRAY_BAR)),
            yaxis2=dict(title=dict(text="Views", font=dict(color=RED_ACCENT)), tickfont=dict(color=RED_ACCENT),
                        overlaying='y', side='right', showgrid=False)
        )
        st.plotly_chart(fig_day, use_container_width=True)

    with col_b:
        st.subheader("Weekly Job Supply")
        st.caption("""
            **The Early Bird Advantage:** This tracks when companies drop new roles. 
            Applying on high-supply days ensures your resume is at the top of the pile.
        """)
        fig_day_supply = px.bar(day_stats, x='day_name', y='Postings', color_discrete_sequence=[GRAY_BAR])
        fig_day_supply.update_layout(height=CHART_HEIGHT, margin=dict(l=10, r=10, t=30, b=0),
                                     xaxis_title="", yaxis_title="Postings")
        st.plotly_chart(fig_day_supply, use_container_width=True)

    with col_c:
        st.subheader("Application Rate (%)")
        st.caption("""
            **The Decisiveness Score:** Measures 'App-to-View' ratio. Higher % means 
            users are moving from browsing to applying.
        """)
        fig_conv = px.line(day_stats, x='day_name', y='Conv %', markers=True, color_discrete_sequence=[RED_ACCENT])
        fig_conv.update_layout(height=CHART_HEIGHT, margin=dict(l=10, r=10, t=30, b=0),
                               yaxis=dict(ticksuffix="%", range=[0, day_stats['Conv %'].max() * 1.3]),
                               xaxis_title="", yaxis_title="Ratio (%)")
        st.plotly_chart(fig_conv, use_container_width=True)
        # Final Pro Tip Box

    # --- STRATEGIC PRO TIP: WEEKLY ---
    # st.success(f"**Pro Tip:** Weekly data shows **{best_day}** is the best day to apply.")
    # 3. Dynamic Pro Tip
    if sweet_spot_day == peak_supply_day:
        st.success(f"**Coach's Strategy:** **{sweet_spot_day}** is the clear winner today—it holds the highest supply and the best efficiency.")
    else:
        st.success(f"**Coach's Strategy:** While **{peak_supply_day}** has the most postings, **{sweet_spot_day}** is your 'Sweet Spot.' Supply remains high, but you'll face **{comp_reduction}% less competition** for the recruiter's attention.")

with tab4:
    # Monthly Aggregation (Ensure this runs inside the tab logic)
    month_stats = filtered_df.groupby('month_name', observed=True).agg({
        'metadata_totalNumberOfView': 'sum',
        'metadata_totalNumberJobApplication': 'sum',
        'title': 'count'
    }).reset_index().rename(columns={'title': 'Postings', 'metadata_totalNumberOfView': 'Views', 'metadata_totalNumberJobApplication': 'Apps'})
    month_stats['Conv %'] = (month_stats['Apps'] / month_stats['Views'] * 100).round(2)
    # --- LOGIC: COMPUTE MONTHLY DYNAMIC INSIGHTS ---

    # 1. Basic Stats
    m_peak_supply_val = month_stats['Postings'].max() if not month_stats.empty else 0
    m_peak_supply_month = month_stats.loc[month_stats['Postings'].idxmax(), 'month_name'] if not month_stats.empty else "N/A"
    m_peak_apps_val = month_stats['Apps'].max() if not month_stats.empty else 1 # Avoid div by zero

    # 2. Split Year
    h2_months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    h1_data = month_stats[~month_stats['month_name'].isin(h2_months)]
    h2_data = month_stats[month_stats['month_name'].isin(h2_months)]

    # Initialize defaults to prevent errors
    is_second_wind = False
    m_comp_reduction = 0
    best_h2_month_name = ""

    # 3. Defensive Calculation
    if not h1_data.empty and not h2_data.empty:
        h1_avg_apps = h1_data['Apps'].mean()
        
        # Get the specific row for the best month in H2
        idx_max_h2 = h2_data['Postings'].idxmax()
        best_h2_month_row = h2_data.loc[idx_max_h2]
        
        best_h2_month_name = best_h2_month_row['month_name']
        
        # The 'Second Wind' Check
        # We use .item() or explicit indexing if we suspect multiple rows, 
        # but usually, month_name is unique.
        supply_check = best_h2_month_row['Postings'] > (m_peak_supply_val * 0.7)
        app_check = best_h2_month_row['Apps'] < h1_avg_apps
        
        is_second_wind = bool(supply_check and app_check)
        m_comp_reduction = round(((m_peak_apps_val - best_h2_month_row['Apps']) / m_peak_apps_val) * 100)

    # --- 2. DISPLAY LOGIC (At the bottom of the script) ---
    col_d, col_e, col_f = st.columns(3)
    
    with col_d:
        st.markdown("### Monthly App Volume")
        st.caption("""
            **Seasonality Radar:** Spot the big hiring waves. In Singapore, peaks often 
            align with 'Post-CNY' shuffles or mid-year 'Q3 Budget' approvals—watch for 
            rising Views to predict coming competition.
        """)
        fig_month = px.bar(month_stats, x='month_name', y='Apps', color_discrete_sequence=[GRAY_BAR], opacity=0.8)
        fig_month.add_scatter(x=month_stats['month_name'], y=month_stats['Views'], name='Views', 
                              yaxis='y2', line=dict(color=RED_ACCENT, width=3))
        
        fig_month.update_layout(
            height=CHART_HEIGHT, margin=dict(l=10, r=10, t=30, b=0),
            showlegend=False, 
            # FIX: Force all months to show
            xaxis=dict(title="", tickmode='linear'), 
            yaxis=dict(title=dict(text="Apps", font=dict(color=GRAY_BAR)), tickfont=dict(color=GRAY_BAR), tickformat=".2s"),
            yaxis2=dict(title=dict(text="Views", font=dict(color=RED_ACCENT)), tickfont=dict(color=RED_ACCENT),
                        tickformat=".2s", overlaying='y', side='right', showgrid=False)
        )
        st.plotly_chart(fig_month, use_container_width=True)

    with col_e:
        st.markdown("### Monthly Job Supply")
        st.caption("""
            **Inventory Forecast:** High supply months represent a 'Buyer's Market'. 
            More choices mean you can be pickier with roles and expect higher response 
            rates as companies race to fill annual headcounts.
        """)
        fig_month_supply = px.bar(month_stats, x='month_name', y='Postings', color_discrete_sequence=[GRAY_BAR])
        fig_month_supply.update_layout(
            height=CHART_HEIGHT, margin=dict(l=10, r=10, t=30, b=0),
            # FIX: Force all months to show
            xaxis=dict(title="", tickmode='linear'), 
            yaxis_title="Postings"
        )
        st.plotly_chart(fig_month_supply, use_container_width=True)

    with col_f:
        st.markdown("### Application Rate (%)")
        st.caption("""
            **The Commitment Metric:** This filters out 'curiosity' clicks. High % 
            months reveal when candidates are most serious about moving—use this to 
            gauge when the most qualified talent is active.
        """)
        fig_month_conv = px.line(month_stats, x='month_name', y='Conv %', markers=True, color_discrete_sequence=[RED_ACCENT])
        fig_month_conv.update_layout(
            height=CHART_HEIGHT, margin=dict(l=10, r=10, t=30, b=0),
            # FIX: Force all months to show
            xaxis=dict(title="", tickmode='linear'), 
            yaxis=dict(ticksuffix="%", range=[0, month_stats['Conv %'].max() * 1.3], title="Ratio (%)")
        )
        st.plotly_chart(fig_month_conv, use_container_width=True)
    # best_month = month_stats.loc[month_stats['Conv %'].idxmax(), 'month_name']
    # st.success(f"**Pro Tip:** Seasonality data shows **{best_month}** is the best month to apply.")
    # # Container for Tips
    # We use a container to keep the tips grouped
    with st.container():
        # 2. Monthly Advice
        if is_second_wind:
            st.info(f"""
                **Seasonal Strategy: The 'Second Wind' Window.** Data shows supply remains strong in **{best_h2_month_row['month_name']}**, 
                but competition has dropped by **{m_comp_reduction}%** compared to the mid-year peak. This is the best time to 
                apply for high-leverage roles while other candidates are resting.
            """)
        else:
            st.info(f"**Seasonal Strategy:** Hiring reaches its absolute peak in **{m_peak_supply_month}**. Prepare your portfolio 1 month early to 'Front-Run' the applicant flood.")
        
# --- 5. COLLAPSIBLE LOGIC EXPLANATION ---
with st.expander("How is the 'Sweet Spot' calculated? (The Strategy Logic)"):
    st.markdown(f"""
    The **Coach's Strategy** uses a **Competitive Arbitrage** logic to find your best ROI:
    
    1. **Identify the Noise Peak:** We find the day with the absolute highest job postings (**{peak_supply_day}**).
    2. **Filter for Opportunity:** We look for other days where job supply is still at least **80%** of that peak.
    3. **Find the Path of Least Resistance:** Among those high-supply days, we select the one with the lowest total applications (**{sweet_spot_day}**).
    4. **Quantify your Edge:** In this case, applying on **{sweet_spot_day}** puts you in front of recruiters with **{comp_reduction}% less competition** than the Tuesday rush.
    
    **The Goal:** Don't just apply when there are the most jobs; apply when you have the highest chance of being seen.
    """)
# --- VISUALIZATION ROW 1: Weekly Volume v 2 end---


# --- Visualization Layout ---

# --- 5. NEW SECTION: SENIORITY MARKET POTENTIAL START---

# --- 5. NEW SECTION: SENIORITY MARKET POTENTIAL ---
st.header("Position like a Pro")
st.caption("Analyzing the Job Title of the **Top 10% (90th Percentile)** to identify sweet spots.")

if not df_seniority_all.empty:
    # 1. FAST FILTERING: Apply current Sidebar filters to the pre-tokenized data
    snr_mask = (
        (df_seniority_all['positionLevels'].isin(selected_positionLevels)) & 
        (df_seniority_all['average_salary'].between(price_range[0], price_range[1]))
    )
    current_snr_df = df_seniority_all[snr_mask]

    # 2. AGGREGATION: Calculate stats for the bubbles
    seniority_stats = current_snr_df.groupby('word').agg(
        Top_Views=('metadata_totalNumberOfView', lambda x: x.quantile(0.9)),
        Top_Apps=('metadata_totalNumberJobApplication', lambda x: x.quantile(0.9)),
        Job_Count=('word', 'count')
    ).reset_index()

    # 3. RANGE FILTER: Apply the Job Volume slider
    seniority_stats_filtered = seniority_stats[
        (seniority_stats['Job_Count'] >= min_vol) & 
        (seniority_stats['Job_Count'] <= max_vol)
    ].copy()

    # Prep clean labels
    seniority_stats_filtered['display_name'] = seniority_stats_filtered['word'].str.upper()

    if not seniority_stats_filtered.empty:
        # 4. VISUALIZATION: Using px.colors.qualitative.Safe
        fig_bubble = px.scatter(
            seniority_stats_filtered,
            x='Top_Views',
            y='Top_Apps',
            size='Job_Count',
            color='word', 
            text='display_name', 
            hover_name='word',
            size_max=60,
            labels={
                'Top_Views': 'Top Tier Views',
                'Top_Apps': 'Top Tier Apps',
                'Job_Count': 'Market Volume'
            },
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig_bubble.update_traces(
            textposition='top center', 
            textfont=dict(size=12, weight='bold'),
            marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.8)
        )
        
        fig_bubble.update_layout(
            height=600,
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(gridcolor='rgba(0,0,0,0.05)', showline=True),
            yaxis=dict(gridcolor='rgba(0,0,0,0.05)', showline=True)
        )

        # Red Dotted Quadrant Lines
        v_median = seniority_stats_filtered['Top_Views'].median()
        a_median = seniority_stats_filtered['Top_Apps'].median()
        
        fig_bubble.add_hline(y=a_median, line_dash="dot", line_color="red", opacity=0.3)
        fig_bubble.add_vline(x=v_median, line_dash="dot", line_color="red", opacity=0.3)

        st.plotly_chart(fig_bubble, use_container_width=True)

        # 5. COACH'S INSIGHT
        with st.container():
            top_comp_word = seniority_stats_filtered.loc[seniority_stats_filtered['Top_Apps'].idxmax(), 'word'].upper()
            st.info(f"**Coach's Reading:** Currently, **{top_comp_word}** roles are seeing the most intense competition in this specific volume range.")
    else:
        st.warning(f"No seniority keywords match the volume range of {min_vol} to {max_vol}.")
else:
    st.error("Seniority data could not be processed. Please check your data source.")


# --- 5. NEW SECTION: SENIORITY MARKET POTENTIAL END---



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
