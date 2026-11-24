-- ============================================================================
-- ORACLE DATABASE 23ai: AI VECTOR SEARCH & HYBRID SEARCH FOR CODE REVIEW PRs
-- ============================================================================

-- 1. Create Table with Native VECTOR Data Type (384 dimensions, FLOAT32)
CREATE TABLE github_pr_reviews (
    pr_id              NUMBER PRIMARY KEY,
    repo_name          VARCHAR2(200),
    pr_title           VARCHAR2(500),
    pr_body_comment    CLOB,
    is_llm_assisted    NUMBER(1),
    task_category      VARCHAR2(50),
    project_age_months NUMBER,
    no_commits         NUMBER,
    no_changed_files   NUMBER,
    pr_size            NUMBER,
    at_review_hrs      NUMBER(10,2),
    at_waiting_hrs     NUMBER(10,2),
    at_change_hrs      NUMBER(10,2),
    time_to_merge_hrs  NUMBER(10,2),
    review_vector      VECTOR(384, FLOAT32)
);

-- 2. Check Memory Footprint using DBMS_VECTOR Memory Advisor
DECLARE
    v_response JSON;
BEGIN
    DBMS_VECTOR.INDEX_VECTOR_MEMORY_ADVISOR(
        INDEX_TYPE     => 'HNSW',
        NUM_VECTORS    => 10000,
        DIM_COUNT      => 384,
        DIM_TYPE       => 'FLOAT32',
        PARAMETER_JSON => '{"neighbors":32}',
        RESPONSE_JSON  => v_response
    );
    DBMS_OUTPUT.PUT_LINE(JSON_SERIALIZE(v_response PRETTY));
END;
/

-- 3. Generate Embeddings Natively Inside Oracle 23ai via ONNX Model
-- (Assumes ONNX model ALL_MINILM_L6_V2 is loaded via DBMS_VECTOR.LOAD_ONNX_MODEL)
UPDATE github_pr_reviews
SET review_vector = VECTOR_EMBEDDING(ALL_MINILM_L6_V2 USING pr_title || ' ' || pr_body_comment AS DATA);
COMMIT;

-- 4. Create In-Memory Neighbor Graph (HNSW) Vector Index
CREATE VECTOR INDEX pr_hnsw_idx ON github_pr_reviews(review_vector)
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE COSINE
WITH TARGET ACCURACY 95;

-- 5. Create Hybrid Vector Index (Combines Keyword Tokenizer + Semantic Vectorizer)
CREATE HYBRID VECTOR INDEX pr_hybrid_idx ON github_pr_reviews(pr_body_comment)
PARAMETERS('MODEL ALL_MINILM_L6_V2');

-- 6. Semantic Similarity Search + Relational Filtering (Replacing Manhattan Distance)
SELECT pr_id, repo_name, task_category, time_to_merge_hrs,
       VECTOR_DISTANCE(review_vector,
           VECTOR_EMBEDDING(ALL_MINILM_L6_V2 USING 'Refactor API handler and add try-catch error handling' AS DATA),
           COSINE
       ) AS semantic_distance
FROM github_pr_reviews
WHERE is_llm_assisted = 0
ORDER BY semantic_distance
FETCH APPROX FIRST 5 ROWS ONLY;

-- 7. Hybrid Search Query (Keyword + Semantic Ranking Fusion)
SELECT DBMS_HYBRID_VECTOR.SEARCH(
    JSON('{
        "hybrid_index_name": "PR_HYBRID_IDX",
        "search_text": "GPT bug fix error handling",
        "return": {"top_n": 5}
    }')
) AS hybrid_results
FROM DUAL;
