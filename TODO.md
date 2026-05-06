# TODO — claude-mcp Improvements

Prioritized backlog of improvements for the private knowledge base MCP server.
Work top-down — items are ordered by priority.

---

## 1. Clean orphaned files from the database on re-ingest

**Problem:** `ingest.py` uses `upsert()`, which adds/updates chunks but never removes
chunks for files that have been deleted or moved. Over time, the DB accumulates
stale entries that pollute search results.

**Goal:** A re-ingest should leave the DB reflecting the *current* state of `DATA_PATH`.

**Approach (keep it simple):**
- Before/after indexing, list all chunk IDs currently in the collection.
- Compare against the set of files actually present on disk.
- Delete chunks whose `source` metadata points to a file that no longer exists.
- Optionally: add a `--clean` flag, or just always reconcile on every run.

**Files to touch:** `src/rag_engine.py`, `ingest.py`

---

## 2. Return the source file in query responses

**Problem:** `ask_knowledge_base` returns concatenated text only. Claude cannot
cite which file each snippet came from, so the user cannot verify or open the
original document.

**Goal:** Each returned chunk should be labeled with its source path (and ideally
the chunk index).

**Approach:**
- In `src/main.py`, read `results['metadatas'][0]` alongside `results['documents'][0]`.
- Format each chunk as something like:
  ```
  [Source: path/to/file.pdf — chunk 3]
  <chunk text>
  ```
- Keep the separator (`---`) between chunks.

**Files to touch:** `src/main.py`

---

## 3. Upgrade the embedding model (English-focused, better quality)

**Problem:** `all-MiniLM-L6-v2` is small, fast, and dated. For English-only
documents we can do significantly better on retrieval quality without going
multilingual.

**Goal:** Swap to a stronger English embedding model.

**Candidates (pick one):**
- `BAAI/bge-base-en-v1.5` — strong general-purpose English model, ~110M params.
- `BAAI/bge-large-en-v1.5` — higher quality, slower, ~335M params.
- `intfloat/e5-base-v2` — also excellent, English-only.
- `mixedbread-ai/mxbai-embed-large-v1` — top-tier, ~335M params.

**Approach:**
- Update `.env`: change `EMBEDDING_MODEL=...`.
- **Important:** changing the model invalidates existing embeddings. After
  switching, run `make clean-all` and re-ingest from scratch.
- Note: `bge`/`e5` models often expect a query prefix (e.g. `"query: ..."` for
  e5, or `"Represent this sentence for searching relevant passages: ..."` for
  bge). Add this in `RagEngine.search()` if using those models.

**Files to touch:** `.env`, possibly `src/rag_engine.py` (for query prefix).

---

## 4. Fix Windows path handling ✅ DONE

**Problem:** The project was built with WSL2/Linux paths in mind
(`/mnt/c/Users/...`). Running natively on Windows requires Windows-style paths
(`C:\Users\...`), and there are several spots where path handling could break:
- `.env` `DATA_PATH` value.
- `chromadb.PersistentClient(path="./chroma_db")` — relative path, depends on CWD.
- File path stored in `metadata["source"]` — backslashes vs forward slashes.
- The chunk ID `f"{file_path}_{i}"` — long Windows paths may have edge cases.

**Goal:** The project should run natively on Windows without WSL.

**Approach:**
- Verify `.env` accepts and resolves Windows paths correctly.
- Use `pathlib.Path` consistently instead of `os.path` string concatenation.
- Normalize paths (`Path.resolve()`) before storing in metadata.
- Make the ChromaDB path absolute and anchored to the project root, not CWD.
- Test the full flow on Windows: ingest → server start → query via Claude.

**Files to touch:** `src/rag_engine.py`, `ingest.py`, `.env`, possibly `Makefile`.

---

## 5. Add re-ranking for better result ordering

**Problem:** Vector similarity returns the top-N closest chunks, but
"closest by cosine distance" is not the same as "most relevant to the question."
A cross-encoder re-ranker scores each (query, chunk) pair directly and reorders
them, typically giving a large precision boost.

**Goal:** After the initial vector search, re-rank results before returning.

**Approach:**
- Retrieve more candidates than needed (e.g. top 20 instead of top 5).
- Use a cross-encoder to score each (query, chunk) pair:
  - `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast, good quality).
  - `BAAI/bge-reranker-base` (higher quality, slower).
- Sort by re-rank score, return top N (e.g. 5).
- Add a config flag to enable/disable re-ranking (cold start cost on first query).

**Files to touch:** `src/rag_engine.py`, `src/main.py`, `pyproject.toml` (new dep).

---

## Notes

- After completing any item, update this file: strike through or remove the item.
- Items 1–4 are independent and can be done in any order. Item 5 depends on
  nothing but is the most invasive change.
- Item 3 forces a full re-ingest, so consider doing it together with item 1
  (which improves the re-ingest experience anyway).
