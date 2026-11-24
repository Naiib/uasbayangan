import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
import statsmodels.formula.api as smf

df = pd.read_csv("dataset_pr_experiment.csv")

# RQ1 & RQ2: Mann-Whitney U Tests
llm = df[df["is_llm_assisted"] == 1]
non = df[df["is_llm_assisted"] == 0]

for col in ["time_to_merge_hrs", "at_review_hrs", "at_waiting_hrs", "at_change_hrs"]:
    stat, p = mannwhitneyu(llm[col], non[col], alternative="less")
    print(f"{col:20s} | LLM Med: {llm[col].median():6.2f}h | Non-LLM Med: {non[col].median():6.2f}h | p-val: {p:.4e}")

# RQ1: Multiple Linear Regression Model (MLRM) with log1p transformation
for col, new_col in [("time_to_merge_hrs", "log_merge"), ("no_commits", "log_commits"),
                     ("pr_size", "log_size"), ("no_changed_files", "log_files"),
                     ("project_age_months", "log_age")]:
    df[new_col] = np.log1p(df[col])

model = smf.ols("log_merge ~ is_llm_assisted + log_commits + log_size + log_files + log_age", data=df).fit()
print(model.summary())
