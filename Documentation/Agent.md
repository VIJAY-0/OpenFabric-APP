# AGENT MODULE

the Agent module-based AI assistant system. 
It includes detailed descriptions of each class, method, design choice, and usage intent.


```
Agent/
├── Agent.py              # Main agent orchestrator
├── Generator.py          # Abstract content generation interface
├── LLM/                  # LLM implementations
│   ├── Gemini.py
│   ├── Ollama.py
│   └── llm.py            # LLM abstract interface
├── Processor.py          # Response interpretation and task executor
├── PromptManager.py      # Loads prompt templates
├── Prompts/              # Prompt files
│   ├── BasePrompt.txt
│   └── ImagePrompt.txt
├── SessionsManager.py    # Caches and stores session state
├── Storage/              # Storage layers
│   ├── DB.py             # Abstract DB interface
│   ├── VectorDB.py       # Mongo + pgvector implementation
└── README.md             # You're here!
```

---

## 1. `Agent.py`

### Class: `Agent`

The `Agent` class acts as the central controller that manages session state, communicates with the chosen LLM backend, interprets and executes model outputs, and connects to external memory and generation systems.

#### **Constructor**

```python
def __init__(self, baseLLM, username, session_id, generator: Generator):
```

- **baseLLM**: String literal to choose between Gemini or Ollama LLMs.
- **username**: Name of the user for tracking sessions.
- **session_id**: If provided, attempts to resume; otherwise generates a new one.
- **generator**: Instance of a class implementing `Generator`, used for producing image and 3D model.

#### **Attributes**

- `self.session_id`: Unique identifier of the current session.
- `self.session_data`: Instance of `SessionData`, stores session-specific outputs.
- `self.llm`: Instance of the LLM being used.
- `Agent._generator`: Static instance of `Generator` shared across all agents.
- `Agent._sessionsManager`: Handles caching and persistence of sessions.
- `Agent._db`: Interface to MongoDB + pgvector storage.

#### **Methods**

- `add_session(session_id)` - Creates a new session or loads from memory/database.
- `get_session_history()` - Retrieves past session history.
- `set_session_history(history)` - Saves current session history to memory.
- `init_baseLLM(baseLLM)` - Instantiates LLM with history.
- `Exec(user_prompt)` - High level Executior, Calls LLM and forwards response to the `Processor`.
- `EXIT()` - Triggers session saving and returns results.
- `return_data()` - Outputs final data: (message, image, object, session_id).
- `save_session()` - Persists session history and semantic embedding.

---

## 2. `Generator.py`

### Abstract Base Class: `Generator`

- This defines the interface for content generation.
- Implementations must define how to produce 2D and 3D assets.

Agent takes a generator object to generae the 2d and 3d content

#### **Methods**

- `generate_image(prompt: str)` - Generate an image based on a descriptive prompt.
- `generate_3drender(prompt: str)` - Generate a 3D object or scene (currently a placeholder).

---

## 3. `Processor.py`

### Class: `Processor`

The `Processor` receives the structured response from the LLM, interprets it using a [State Machine Pattern](./"Processor_State_Machine.md"), and executes the required system-level action.

#### **States Enum**

```python
States = {
    EXIT: 0,
    MEM_RECALL: 1,
    IMAGE: 2,
    MODEL: 3,
    QUERY: 4,
   }
```

#### **Constructor**

```python
def __init__(self, session_data, generator, session_manager, db,baseLLM):
```

- Sets up access to all core modules for memory, LLM, generation, and session state.

#### **Methods**

- `process(llm_response)` - Entry point. Parses JSON, evaluates `state`, and dispatches handler.

- `exit()` - Finalizes session with summary.
- `recall_from_memory()` - Retrieves previous session with similar intent.
- `generate_image()` - Generates image using LLM + image generator.
- `generate_model()` - Placeholder for 3D model support.
- `process_query()` - Stores user's final query for retrieval.

- `HIGHLY extensible can add more features`.
---

## 4. `PromptManager.py`

### Class: `PromptManager`

Manages prompt templates and loads them from files at initialization.

#### **Attributes**

- `_prompts`: Class-level dictionary storing loaded templates.

#### **Methods**

- `load_prompts()` - Loads `BasePrompt.txt` and `ImagePrompt.txt` into memory.
- `get(key)` - Returns prompt by key name.
- `get_base_prompt()` - Shortcut for retrieving the base prompt for new sessions.

Prompt Sources:

- `Prompts/BasePrompt.txt`
- `Prompts/ImagePrompt.txt`

---

## 5. `SessionsManager.py`

### Class: `SessionManager`

Provides memory-caching and retrieval of session history. All sessions are stored in `_sessions` for fast access.

#### **Attributes**

- `_sessions`: Dict storing session\_id → message history.
- `_db`: Database interface (`VectorDB`) for persistent storage.
- `_prompt_manager`: Loads and provides base prompts.

#### **Methods**

- `add_session(session_id)` - Loads session from memory or database, or initializes new.
- `generate_session_id()` - Generates a new UUID.
- `load_session_history(session_id)` - Loads history from DB into cache.
- `get_session_history(session_id)` - Gets history from cache or DB.
- `set_session_history(session_id, history)` - Saves current history in memory.
- `save_session(username, session_id, image_desc, summary)` - Commits full session to DB.

### Class: `SessionData`

Encapsulates and tracks the runtime state of a session, including generated content.

#### **Attributes**

- `session_id`, `username`, `message`, `IMAGE`, `OBJECT`, `image_description`, `summary`, `current_prompt`

#### **Methods**

- `set(...)` - Flexible update for partial data (e.g., new message or image).

---

## 6. `LLM/llm.py`

### Abstract Base Class: `LLM`

Interface for building pluggable LLM backends.

#### **Message Format**
- Message object stores the interaction between user(Agent from our side) and the model (LLM ) in a formatted manner which is easy to acess

```python
class Message(TypedDict):
    role: Literal["model", "user"]
    content: str
```

- History of conversation is stored as list of Messages

```python
    history = [
        Message(role='user' , content='prompt1')
        Message(role='model' , content='response1')
        Message(role='user' , content='prompt2')
        Message(role='model' , content='response2')
    ]
```

#### **Methods**

- `generate_content(prompt)` - For one-off completions.
- `prompt(history)` - Interacts with LLM using complete message history.
- `get_history()` - Returns running memory of chat.

---

## 7. `Storage/DB.py`
### Abstract Base Class: `DB`

Contract class for unified database access.

#### **Methods (Abstract)**

- `save_session(username, session_id, image_desc, history, summary)`
- `get_image_description(intent, session_id)`
- `get_conversation_history(intent, session_id)`

---

## 8. `Storage/VectorDB.py`

### Class: `VectorDB(DB)`

Implements session storage and context based retrival using:

- **MongoDB** for structured data (e.g., history, images)
- **PostgreSQL + pgvector** for semantic similarity search

#### **Subcomponents**

##### Class: `SessionsStore`

Handles MongoDB connection and queries (used fr storing session conversatio history and other metadata).
- `get_session_history(session_id)`
- `get_image_description(session_id)`
- `save_session(session_id, image_description, history)`

##### Class: `VectorStore`

Manages vector-based search and storage in PostgreSQL.

- `get_encoder()` - Returns sentence transformer instance.
- `get_session_id(intent)` - Finds closest matching session.
- `save_session(session_id, username, summary)` - Saves session embedding.
- `init_table()` - Ensures `chat_index` table and pgvector extension are present.

---


## 🔄 Flow of Execution

```text
User Input → Agent.Exec()
                loop:
                    ↳ UserPrompt/ProcessorResponse→LLM (Gemini/Ollama)
                        ↳ JSON State Response
                        ↳ Processor.process()
                            ↳ Action (Generate, Recall, etc)
                ↳ Return: (message, image, object, session_id)
```

---

## 📌 TODO list

- Use cache eviction (LRU) in `SessionManager`
- Use real conversation summary for `summary` field
- Validate LLM output structure before parsing JSON
- Add retry/error handling for DB/LLM/API failures

---
