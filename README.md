# Eksperimen Empiris: Dampak LLM pada Proses Code Review & Integrasi Oracle Database 23ai Vector Search

Repositori ini berisi artefak penelitian empiris berbasis metode **ATM (Amati, Tiru, Modifikasi)** dari studi *The Impact of Large Language Models (LLMs) on Code Review Process* (Collante et al., 2025) yang diintegrasikan dengan arsitektur **Oracle Database 23ai AI Vector Search & RAG**.

## Struktur Repositori
- `01_fetch_github_data.py`: Skrip akuisisi metadata dan timeline Pull Request via GitHub REST API.
- `02_oracle_vector_setup.sql`: Skrip DDL/DML Oracle 23ai (`VECTOR` data type, `HNSW` index, `Hybrid Vector Search`, dan `DBMS_VECTOR` Memory Advisor).
- `03_statistical_analysis.py`: Skrip uji non-parametrik *Mann-Whitney U* dan *Multiple Linear Regression Model (MLRM)*.
- `04_rag_code_reviewer.py`: Prototipe *Agentic RAG Code Reviewer* berbasis konteks historis PR.
- `dataset_pr_experiment.csv`: Dataset kurasi mandiri (120 PR ter-merge dari 4 repositori open-source).
- `experiment_results_charts.png`: Visualisasi distribusi waktu resolusi (RQ1) dan perbandingan latensi per fase PR (RQ2).
- `PROMPTS.md`: Kumpulan prompt terstruktur yang digunakan selama eksperimen.

## Cara Menjalankan
1. Install dependensi Python:
   ```bash
   pip install pandas numpy scipy statsmodels matplotlib seaborn requests
   ```
2. Jalankan analisis statistik:
   ```bash
   python 03_statistical_analysis.py
   ```
3. Jalankan skrip `02_oracle_vector_setup.sql` pada instance **Oracle Database 23ai Free** atau **Oracle LiveLabs**.
