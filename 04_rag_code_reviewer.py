import os
import json
import numpy as np
import pandas as pd

# Simulated / Local RAG Pipeline mimicking Oracle 23ai Vector Search + LLM Code Reviewer
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)

def run_rag_code_review(pr_diff_text, pr_title, top_k_context):
    prompt = f"""You are a Senior Software Engineer performing an automated Pull Request Code Review.
Use the retrieved historical PR review context from Oracle Database 23ai Vector Search to ground your review.

[RETRIEVED HISTORICAL CONTEXT]
{top_k_context}

[TARGET PULL REQUEST]
Title: {pr_title}
Code Diff / Description:
{pr_diff_text}

Provide a structured review covering:
1. Potential Bugs / Edge Cases
2. Code Enhancement & Refactoring Suggestions
3. Missing Error Handling or Test Coverage
4. Merge Readiness Score (1-10)
"""
    return prompt

if __name__ == "__main__":
    df = pd.read_csv("dataset_pr_experiment.csv")
    sample_pr = df[df["is_llm_assisted"] == 1].iloc[0]
    context_examples = "\n".join(
        f"- PR #{r.pr_id} ({r.task_category}): {r.pr_title} -> {r.pr_body_comment}"
        for _, r in df.head(3).iterrows()
    )
    generated_prompt = run_rag_code_review(sample_pr["pr_body_comment"], sample_pr["pr_title"], context_examples)
    print(generated_prompt)
