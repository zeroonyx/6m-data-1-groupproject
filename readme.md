# Group Project: Job Market Optimization Analysis
**Team Members:** *in alphabetical order by last name*
 - Li Zhongyi (Ethan)	
 - Lin Minghui (Reeve)	
 - Mao Jianwen (Tony)	
 - Nainar Mohamed (Nainar)	
 - Yang Shicong (Shicong)

**Persona:** 
 - Persona D — The Job Seeker Optimisation Coach

## Project Overview
This project analyzes job posting metadata to provide data-driven insights for job seekers. We focus on timing, title optimization, and identifying low-competition niches in the market.

## Rerferences
1. https://docs.google.com/document/d/1Jm8-oaM8JDiAe1Z044rTMMhMGb8Cg6bIsLIZKBnCrwM/edit?tab=t.0


## Persona D — The Job Seeker Optimisation Coach
"I help job seekers compete. I want to know: when to apply, what title patterns get the most views, and where applications are most likely to convert."

### Business Questions
1. **When to Apply?** Which days of the week and months of the year do job postings receive the most views and applications?
2. **Title Optimization?** Do certain keywords in job titles (e.g. Senior, Junior, Lead) correlate with higher views and application counts?        
3. **Low-Competition Niches?** Which primary job categories have the lowest applications-per-vacancy ratio, indicating less competition?

### Additional Questions to Explore
4) **"Hidden Gems"—categories with a high applications-per-vacancy ratio but low total applications, suggesting they are overlooked by job seekers.**
5) **"Sweet Spot"—categories where the salary is high but the competition (apps-per-vacancy) is relatively low.**
6) What skill set is required for the job?

### Stretch challenges (if you finish early)
 - Salary band width analysis: For each primary_category, compute salary_maximum - salary_minimum using NumPy. Which categories have the widest bands? What might that signal about negotiation room?
- "Ghost jobs" revisited: Using Pandas date arithmetic (metadata_expiryDate - metadata_originalPostingDate), identify postings open for more than 90 days with zero applications. How prevalent are they? Which categories and levels?
- Title keyword co-occurrence: Build a frequency table of two-word title bigrams (split title on spaces, then use pd.Series(bigrams).value_counts()). Which bigrams are trending upward over time?
- Cohort analysis: Group jobs by posting quarter. For each cohort, track median salary, median minimumYearsExperience, and application rate. Has the market become more or less demanding over time?
- Agency concentration index: For each primary_category, compute the share of jobs posted by the top 3 agencies. Build a "concentration index" and rank categories from most agency-dominated to least.

## Data Dictionary
<details>
<summary>Click to view full column metadata</summary>

| Column | Type | Notes |
| :--- | :--- | :--- |
| **categories** | `str (JSON)` | JSON array of categories. Needs parsing. |
| **employmentTypes** | `str` | Type of contract (Permanent, Full Time, etc.) |
| **metadata_originalPostingDate** | `date` | Original date the job was listed. |
| **metadata_repostCount** | `int` | Signal of hard-to-fill roles. |
| **metadata_totalNumberOfView** | `int` | Total views received. |
| **metadata_totalNumberJobApplication** | `int` | Total applications received. |
| **positionLevels** | `str` | Seniority (Entry, Executive, Manager, etc.) |
| **salary_minimum / maximum** | `int` | Monthly salary range. |
| **average_salary** | `float` | Mean of min/max salary. |

*(Table truncated for brevity—paste the full version here)*
</details>

## Technical requirements (your notebook must demonstrate ALL of these)
To prove you stretched your Python muscles, your final notebook must include:

- [ ] At least one NumPy operation applied to a column extracted as an array (e.g. np.mean, np.percentile, np.std, boolean mask, or a normalisation formula).
- [ ] At least one Pandas groupby with a meaningful aggregation (not just .count()) — e.g. .agg({'col': ['mean', 'median']}).
- [ ] At least one missing-value handling step — isnull() inspection plus a .fillna(), .dropna(), or .replace() decision that is documented in a Markdown cell.
- [ ] At least one string/text operation on the title or positionLevels or categories column (.str.contains, .str.extract, .str.upper, etc.).
- [ ] At least one date/time operation using the metadata_originalPostingDate column (dt.month, dt.year, dt.to_period, etc.).
- [ ] At least two different chart types (e.g. bar + boxplot, histogram + scatter, line + heatmap) — each with a title, axis labels, and a one-sentence interpretation comment below.
- [ ] A documented data-cleaning step in a Markdown cell: what you removed, why, and how many rows were affected.

## Deployment for Streamlit
**Create Env**

```bash
conda env create -f environment.yml
```

**Activate the environment**

```bash
conda activate streamlit_app
```
