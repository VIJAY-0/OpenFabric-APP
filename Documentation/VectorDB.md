# 📘 Agent Storage Module Documentation

This module provides a scalable and modular implementation for managing conversational session data using **MongoDB** and **PostgreSQL with pgvector**, supporting advanced semantic search and persistent storage of interactions.

---

## 🔶 Abstract Base Class: `DB`

An abstract interface that enforces consistent implementation across all storage backends.

```python
class DB(ABC):
```

### Abstract Methods

#### `__init__(self)`

Initializes the storage class. Must be implemented in subclasses.

#### `save_session(self, username, session_id, image_desc, history, summary)`

Saves a session's data into the underlying storage systems.

- `username (str)`: Username associated with the session.
- `session_id (str)`: Unique session ID.
- `image_desc (str)`: Description of the image tied to the session.
- `history (List[Any])`: Chat history for the session.
- `summary (str)`: Summary used for semantic search.

#### `get_image_description(self, intent, session_id)`

Retrieves the image description for a session, optionally inferred via semantic intent.

- `intent (str)`: User’s intent (semantic query).
- `session_id (str)`: Session ID (optional if intent is given).

#### `get_conversation_history(self, intent, session_id)`

Retrieves full conversation history, optionally inferred via intent.

---

## 🔷 Class: `VectorDB(DB)`

Implements `DB` using:

- MongoDB for session data.
- PostgreSQL + pgvector for semantic session retrieval.
- SentenceTransformers for embeddings.

### Class Attributes

- `_vectorStore`: Shared instance of `VectorStore`.
- `_sessionsStore`: Shared instance of `SessionsStore`.

### Methods

#### `__init__(self)`

Initializes the MongoDB and Vector DB backends if not already initialized (singleton-style).

#### `save_session(cls, username, session_id, image_desc, history, summary)`

Saves session data:

- Stores history and image description in MongoDB.
- Stores semantic summary embedding in pgvector.

#### `get_image_description(cls, intent="", session_id="")`

If `intent` is provided, infers session ID via semantic match. Retrieves image description from MongoDB.

#### `get_conversation_history(cls, intent="", session_id="")`

Similar to `get_image_description`, but returns full chat history.

---

## 🔷 Class: `SessionsStore`

Encapsulates all MongoDB operations.

### Class Attributes

- `_client`: MongoDB connection.
- `_db`: MongoDB database instance.

### Methods

#### `__init__(self)`

Initializes MongoDB client using environment variables:

- `MONGO_HOST_NAME`
- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`

#### `get_session_history(cls, session_id)`

Fetches chat history for a session.

- `session_id (str)`

Returns:

- `List[Any]`: Parsed conversation history.

#### `get_image_description(cls, session_id)`

Fetches stored image description.

- `session_id (str)`
- Returns: `str`

#### `save_session(cls, session_id, image_description, history)`

Stores/updates the session record.

- `history` is serialized as JSON.

---

## 🔷 Class: `VectorStore`

Encapsulates PostgreSQL + `pgvector` and sentence embedding logic.

### Class Attributes

- `_pool`: PostgreSQL connection pool (`SimpleConnectionPool`).
- `_encoder`: Instance of `SentenceTransformer`.

### Methods

#### `__init__(self)`

Initializes:

- Connection pool to PostgreSQL using environment variables:
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Embedding model: `"all-MiniLM-L6-v2"`
- Creates `chat_index` table if not present.

#### `init_table(cls)`

Ensures `vector` extension and `chat_index` table exist:

```sql
CREATE TABLE IF NOT EXISTS chat_index (
    no SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    embedding VECTOR(384)
);
```

#### `get_encoder(cls)`

Returns the sentence transformer model.

#### `get_conn(cls)`

Fetches a connection from the pool.

#### `get_session_id(cls, intent)`

Returns the most relevant session using semantic similarity on `intent`.

- Encodes `intent` → 384D vector.
- Performs nearest neighbor search:

```sql
SELECT session_id
FROM chat_index
ORDER BY embedding <#> %s::vector
LIMIT 1;
```

Returns: `session_id (str)`

#### `save_session(cls, session_id, username, summary)`

Encodes the summary and saves/upserts into `chat_index`.

- On conflict (duplicate session\_id), updates username and embedding.

---

## 🧠 Design Highlights

| Component       | Backend               | Role                                              |
| --------------- | --------------------- | ------------------------------------------------- |
| `SessionsStore` | MongoDB               | Persistent session history + metadata             |
| `VectorStore`   | PostgreSQL + pgvector | Semantic session lookup via embeddings            |
| `VectorDB`      | Hybrid                | Facade combining both stores under `DB` interface |

### ♻ Embedding Model

- [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
  - Fast + decent quality (384-dim)
  - Enables efficient vector search with pgvector

### ♻ Reusability

- Singleton pattern ensures resources (DB connections, encoder) are not duplicated across sessions.

### 📦 Environment Variables

These must be configured in your environment before launching the system:

```env
# MongoDB
MONGO_HOST_NAME=localhost
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=pass123

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_DB=myvector
```

---

## 🧪 Testing / Sample Use

```python
VectorDB.save_session("user1", "sess_001", "This is a cat", [{"q": "hello", "a": "hi"}], "chat about cats")

VectorDB.get_image_description(session_id="sess_001")

VectorDB.get_conversation_history(intent="talked about cats")
```

---

## 🚰 Future Improvements

- Add caching for frequent session lookups.
- Include image embedding support.
- Add expiration / archival for old sessions.
- Implement deletion or anonymization methods for privacy compliance.

