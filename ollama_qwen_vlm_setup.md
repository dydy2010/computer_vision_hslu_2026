# Ollama + Qwen VLM Setup (Local)

## Short Answer
You install and run **Ollama in the terminal**. The notebook only needs the **Python API client** to call the local Ollama server. You do **not** need to install Ollama inside the notebook.

## Step-by-step flow (beginner-friendly)
1. **Install Ollama (system-level)**
   - Concept: Ollama is a local server that runs models on your machine.
   - Task: Install it once on your OS.
   - Command (Linux):
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```

2. **Start the Ollama server**
   - Concept: The notebook talks to the running server.
   - Task: Start Ollama in a terminal.
   - Command:
     ```bash
     ollama serve
     ```
    - Note: `ollama serve` starts the server for all models. You do **not** pass a model name here.
   - Keep this terminal open while you run the notebook.

3. **Stop the Ollama server (when finished)**
   - Concept: Stopping the server frees GPU/CPU memory.
   - Task: Stop Ollama when you are done for the day or need memory back.
   - Command (in the same terminal):
     ```bash
     # Press Ctrl+C
     ```

4. **Pull the official Qwen VLM model**
   - Concept: Pull = download the model once.
   - Task: Choose one model and download it.
   - Recommended (matches this project):
     ```bash
     ollama pull qwen3-vl:4b
     ```
   - Alternative (if you prefer another model):
     ```bash
     ollama pull qwen3.5:4b
     ```
   - Optional check:
     ```bash
     ollama list
     ```

5. **Install the Ollama Python client (inside your notebook environment)**
   - Concept: The client is just a thin API wrapper.
   - Task: Install it once in your venv.
   - Command (in a notebook cell):
     ```python
     !pip install -q ollama
     ```

6. **Use the model in the notebook**
   - Concept: The notebook sends images to the local Ollama server.
   - Task: Use the client with `ollama.chat(..., images=[...])`.
  - Example: set the model name to match what you pulled (this project uses `qwen3-vl:4b`).

## Quick checklist
- Ollama installed? ✅
- Ollama server running? ✅
- Model pulled? ✅
- Python client installed in the notebook? ✅

If you want, I can add a short troubleshooting section for common errors (port, model not found, or server not running).