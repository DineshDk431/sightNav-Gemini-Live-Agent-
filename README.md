<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg?style=flat-square" alt="Status" />
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat-square" alt="Python Version" />
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg?style=flat-square" alt="UI Streamlit" />
  <img src="https://img.shields.io/badge/AI-Gemini_2.5_Flash-orange.svg?style=flat-square" alt="AI Gemini" />
</div>

<br />

# 👁️ SightNav Agent Control Center V3
**Elite Agentic AI Desktop Navigator with Vision, Audio, and Semantic Memory**

SightNav is a state-of-the-art multimodal AI agent designed to seamlessly navigate, reason, and execute complex workflows on any desktop environment. Combining the raw power of **Google Gemini 2.5 Flash**, **OpenCV Set-of-Mark**, and an advanced **Tri-Reasoning Agent Architecture**, SightNav transforms natural language text or voice commands into localized precise screen actions.

This repository proudly features **V3** of the architecture, representing a massive leap in agentic cognitive abilities by integrating a Safety Gatekeeper, a Reflection Engine, Semantic Long-Term Memory (FAISS), and an interactive Real-Time Control Dashboard built with Streamlit.

---

## ✨ Key Features & Capabilities

- 🛡️ **Intelligent Safety Gatekeeper (SafetyAgent):** Evaluates user intents before execution. Blocks high-risk commands instantly or enforces a Human-in-the-Loop (HITL) step for medium-risk actions using voice confirmation.
- 🖼️ **Set-of-Mark (SoM) Visual Grounding:** By merging Python's screenshot capabilities with OpenCV bounding-box drawing, the agent identifies interactive elements with high coordinate precision.
- 🧠 **Semantic RAG Memory (MemoryManager):** Leverages `faiss-cpu` and `sentence-transformers` for persistent, rule-based Semantic Memory. The agent *learns* from past mistakes and continuously improves.
- 🗣️ **Seamless Voice I/O (AudioAgent):** Supports Gemini Live Voice Streaming. Talk to the agent, give it commands, and hear it speak its analysis back in real-time (`PyAudio`).
- 🤖 **Tri-Reasoning Consensus (VisionAgent & ReflectionAgent):** Complex step-by-step reasoning logic that verifies its own thoughts before attempting macro-level tasks on the OS (`pyautogui`).
- 🎛️ **Streamlit Control Dashboard:** A polished, modern UI for monitoring the agent's monologue, inspecting bounded visual screenshots, checking RAM rules, and managing agent status.

---

## 🏗️ System Architecture Flow

The execution cycle mimics a high-level cognitive loop, processing commands step-by-step:

1. **Perception & Intent:** The `AudioAgent` or UI captures user intent (Voice or Text).
2. **Security Evaluation:** The `SafetyAgent` evaluates the risk level (Safe, Warning+HITL, Blocked).
3. **Visual Grounding:** The Screen Capture module bounds elements structurally leveraging `OpenCV` Set-of-Mark (SoM).
4. **Memory Retrieval (RAG):** The `MemoryManager` queries FAISS for previously learned rules based on the user's intent to avoid historic failures.
5. **Planning & Consensus:** The `VisionAgent` takes the SoM image, coordinates map, rules, and intent to compute a grounded step-by-step sequence.
6. **Execution:** The `Executor` executes native OS automation steps (Mouse/Keyboard).
7. **Reflection:** If the user reports the action failed, the `ReflectionAgent` stores the failure as a new embedded FAISS rule to prevent repeats.

---

## 📂 Project Structure

```text
sightnavi/
├── data/
│   └── long_term_memory.json   # FAISS persistent reasoning store
├── src/
│   ├── agents/
│   │   ├── audio_agent.py      # Voice intent handling and Text-To-Speech
│   │   ├── reflection_agent.py # Feedback looping and rule generation
│   │   ├── safety_agent.py     # Intent screening & HITL handler
│   │   └── vision_agent.py     # Main Multi-modal Logic Controller
│   ├── tools/
│   │   ├── executor.py         # PyAutoGUI execution abstraction
│   │   └── screen_capture.py   # Raw screenshot handling
│   └── utils/
│       ├── logger.py           # CLI formatting & structured logging
│       ├── memory_manager.py   # FAISS RAG and sentence-transformers logic
│       └── vision_utils.py     # OpenCV Set-of-Mark drawing
├── app.py                      # V3 Streamlit Output UI & Dashboard
├── main.py                     # Headless/CLI Orchestrator
├── requirements.txt            # Project Dependencies
└── .env                        # Credentials (GEMINI_API_KEY)
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- Windows OS (For `pyautogui` mouse scaling functions)
- A valid Google Gemini API Key

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-username/sightnavi.git
cd sightnavi

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your Gemini API Key:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 💻 Usage Instructions

You can run SightNav in two distinct modes based on your workflow needs:

### 1. The Dashboard (UI Mode)
Run the Streamlit frontend for the complete visual experience, perfect for monitoring the reasoning loop and executing localized commands.

```bash
streamlit run app.py
```
- A browser window will open at `http://localhost:8501`.
- View the **Action Logs**, monitor the **Semantic Memory RAM**, and execute visually via the **Agent's Vision** bounding box UI.

### 2. The Orchestrator (CLI Headless Mode)
Run the pure Python backend script to interface seamlessly via the console and Voice commands.

```bash
python main.py
```

---

## 🧪 Testing & Future Roadmap

- **Multi-OS Support:** Enhance coordinates translation scaling for Unix/macOS environments.
- **Deep Web-Nav Agents:** Embed specialized Playwright agents for complex non-OS browser actions.
- **Memory Optimization:** Upgrade FAISS database chunks for enterprise-scale semantic storage caching.

---

<div align="center">
  <i>Architected with passion by the ultimate AI Software Engineering Team. </i>
</div>
