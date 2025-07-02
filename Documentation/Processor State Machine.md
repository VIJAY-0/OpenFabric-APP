# 📘 Processor State Machine - README

This document explains the **state machine-based design** of the `Processor` class in the AI Agent framework. The Processor interprets structured JSON outputs from the LLM and determines the next course of action based on predefined states. This design pattern enables a modular and extensible architecture, empowering the LLM to control execution flow through explicit state transitions.

---

## 🔁 Finite State Machine Overview

The `Processor` uses a fixed set of states represented by an internal `Enum`, where each state corresponds to a specific system-level operation.

### State Enum Definition
```python
class States(Enum):
    EXIT = 0
    MEM_RECALL = 1
    IMAGE = 2
    MODEL = 3
    QUERY = 4 #currently unused , but can be integrated by changing the base prompt
```

Each LLM output is expected to include a top-level key:
```json
{
  "state": 2,
  ...additional_keys
}
```

---

## 🧠 LLM-Controlled State Transitions

The LLM responds with structured JSON that includes:
- `state`: an integer mapped to a specific `States` value.
- Optional metadata fields depending on the state.

These responses are preprocessed, parsed, and dispatched to corresponding handler methods like `generate_image`, `recall_from_memory`, etc.

---

## 🧩 State Details

### 🔚 0. EXIT
```json
{
  "state": 0,
  "summary": "This is a session summary."
}
```
- **Effect**: Finalizes session, saves history, and returns results.
- **Processor Method**: `exit(resp)`

---

### 🧠 1. MEM_RECALL
```json
{
  "state": 1,
  "data": { "intent": "neon cyberpunk city" }
}
```
- **Effect**: Uses `VectorDB` to find semantically similar sessions via `intent`.
- **Processor Method**: `recall_from_memory(resp)`

---

### 🖼️ 2. IMAGE
```json
{
  "state": 2,
  "image": "A glowing city in a storm, seen from the mountains."
}
```
- **Effect**: Generates an image using the prompt combined with templates.
- **Processor Method**: `generate_image(prompt)`

---

### 🧱 3. MODEL (Planned)
```json
{
  "state": 3,
  "model": "Generate a wireframe of a robotic arm."
}
```
- **Effect**: Placeholder for future 3D model generation.
- **Processor Method**: `generate_model(prompt)`

---

### 🗣️ 4. QUERY  [Unused State ] 
```json
{
  "state": 4,
  "query": "would you like to add something else ? !"
}
```
- **Effect**: Stores message to be returned as final user response.
- **Processor Method**: `process_query(resp)`


---

## 🔄 Example Execution Flow

```text
1. User prompt → Agent.Exec()
2. LLM → JSON with state = 2 (IMAGE)
3. Processor → Creates a vivid imagePromtp and generates image : generate_image()
5. LLM → JSON with state = 3 (MODEL)
6. Processor → Creates a 3DModel fromprevioulsy generated image: generate_model()
7. LLM → JSON with state = 0 (EXIT)
8. Processor → Exits the Execution: exit()
9. Agent returns the results to user :Agent.EXIT()
```

---

## ✅ Benefits of FSM in LLM-Agent Design

| Feature                | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| **Deterministic**      | Ensures predictable behavior from loosely structured LLM output              |
| **Modular**            | Easily extensible to new states                                              |
| **LLM as Controller**  | Gives control to LLM to dynamically switch actions                          |
| **Interpretable**      | Logs and output are easy to trace and debug                                 |

---

## 🔧 Developer Notes

- Always ensure LLM output is **valid JSON**. Preprocessing removes ``` wrappers.
- Extend `States` Enum and `process()` if adding new capabilities.
- Can integrate retry/backoff logic in case of API/DB failures.
- All states assume a JSON schema – validation could be added to enforce structure.

---

## 📈 Future Improvements

- [ ] Add `STATE_VALIDATOR` for output format robustness
- [ ] Introduce feedback state for user confirmations

---

## 🧭 Summary

This state machine-based design pattern makes the AI agent **modular**, **interpretable**, and **scalable**. By delegating state transitions to the LLM, the system supports rich interactivity and easy expansion.

