# 🧠 Memory System: Working and Recall Mechanism

This section explains how memory works in the `VectorDB` architecture, focusing on storing, embedding, and recalling conversational context.

---

## 💾 Memory Storage Overview

Memory is composed of two parallel layers:

### 1. **MongoDB (SessionsStore)**

- Stores raw data:
  - Session ID
  - Image Description
  - Full Chat History (as JSON)

### 2. **PostgreSQL + pgvector (VectorStore)**

- Stores semantic summaries as vector embeddings
  - Session Ids for sessions
  - Timestamps for filtering against it
  - username
  - **Semantic Embeddings for recall**
  ```sql
   CREATE TABLE IF NOT EXISTS chat_index
    (
      no SERIAL PRIMARY KEY,
      session_id TEXT UNIQUE NOT NULL,
      username TEXT NOT NULL,
      timestamp TIMESTAMP DEFAULT NOW(),
      embedding VECTOR(384)
    );
   ```

- Enables intent-based semantic recall

---

## 🧠 How Memory is Written (Saved)

When a session is complete, the following occurs:

```python
VectorDB.save_session(username, session_id, image_desc, history, summary)
```

### ➕ What Happens Internally:

1. **Session Store**
   - Stores the full conversation and image metadata in MongoDB using the session ID.
   ```python
         collection.replace_one({"_id": session_id},{"_id":session_id, "history": text,"image_description":image_description}, upsert=True)
   ```


2. **Vector Store**
   - Encodes the `summary` string into a 384-dimensional vector using SentenceTransformer.
   ```python
       embedding = encoder.encode(summary)  # returns a 384-dim NumPy array
   ```
   - Saves this vector embedding into the `chat_index` table in PostgreSQL.
   ```sql
      INSERT INTO chat_index (session_id, username, embedding)
      VALUES ('session_id', 'username', ARRAY[...]) -- 
      ON CONFLICT (session_id) DO UPDATE
         SET username = EXCLUDED.username,
         embedding = EXCLUDED.embedding;
   ```
---

## 🔁 How Memory is Recalled

The system can recall memory in two ways:

### A. **By Direct Session ID**

   ```python
   VectorDB.get_conversation_history(session_id="sess_001")
   ```

- Direct MongoDB lookup by ID.
   
   ```python
      query = {"_id":session_id}
      document = collection.find_one(query)
      return document["image_description"]
   ```
- Returns exact image description or chat history.

### B. **By Intent (Semantic Recall)**

   ```python
      VectorDB.get_conversation_history(intent="talked about cats")
   ```
   
   ### ⚙ What Happens Internally:

   1. The input `intent` is encoded into a vector using the same transformer model.
      ```python
         embedding = encoder.encode(summary)  # returns a 384-dim NumPy array
      ```
   2. A similarity search is run against `chat_index`:
      ```sql
      SELECT session_id
      FROM chat_index
      ORDER BY embedding <#> %s::vector
      LIMIT 1;
      ```
   3. The closest matching `session_id` is retrieved.
   4. That session ID is then used to fetch:
      - Image Description → `get_image_description(...)`
      - Chat History → `get_conversation_history(...)`

---

## 🔍 Semantic Vector Search: Why It Works

- pgvector provides `<#>` operator for cosine distance.
- Sentence embeddings from the same model ensure alignment.
   ```python
   SentenceTransformer("all-MiniLM-L6-v2")
   ```
- Allows fuzzy retrieval of sessions even if user phrasing changes.

---

## 🔐 Consistency & Determinism

- The same `summary` always maps to the same vector.
- Using the same model (`all-MiniLM-L6-v2`) ensures repeatability.

---

## 📌 Summary

| Action | Layer              | Method                     | Purpose                        |
| ------ | ------------------ | -------------------------- | ------------------------------ |
| Save   | MongoDB            | `save_session`             | Stores raw history & metadata  |
| save   | pgvector           | `save_session`             | Stores semantic summary vector |
| Recall | pgvector → MongoDB | `get_session_id` → `get_*` | Semantic fetch by intent -> ID |
| Recall | MongoDB            | `get_*`                    | ID -> Direct fetch by ID       |

---
