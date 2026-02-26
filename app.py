"""
SightNav — Streamlit Dashboard (V2)
===================================
Replaces main.py. Provides a sleek local web interface for the 
SightNav Agentic loop. Displays live annotated screenshots,
logs, and user controls.

Run with: streamlit run app.py
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

from src.utils.logger import Logger
from src.tools.screen_capture import capture_screen
from src.tools.executor import execute_plan
from src.agents.vision_agent import VisionAgent
from src.agents.reflection_agent import ReflectionAgent
from src.utils.vision_utils import apply_set_of_mark, draw_target_circle
from src.utils.memory_manager import MemoryManager

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="SightNav AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode hacking
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .status-online { color: #00FF00; font-weight: bold; }
    .status-offline { color: #FF0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Session State Mapping ---
if 'agent_running' not in st.session_state:
    st.session_state.agent_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'latest_image' not in st.session_state:
    st.session_state.latest_image = None
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False

# --- Helper functions ---
def log_ui(msg: str):
    """Pushes a log to the UI list and print"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {msg}")
    Logger.info(msg)

@st.cache_resource
def init_system():
    load_dotenv()
    log_ui("Initializing Agent subsystems...")
    vision = VisionAgent()
    reflection = ReflectionAgent()
    memory = MemoryManager()
    log_ui("Subsystems Online.")
    return vision, reflection, memory

# --- Main UI Build ---
def main():
    st.title("👁️ SightNav Agent Control Center")
    st.caption("A locally-hosted multimodal UI navigation system. Powered by Gemini 2.5 Flash & OpenCV.")

    # Initialize Core singletons
    try:
        vision, reflection, memory = init_system()
        if not st.session_state.system_initialized:
            st.session_state.system_initialized = True
    except Exception as e:
        st.error(f"Failed to boot logic: {e}")
        st.stop()

    # -- Sidebar --
    with st.sidebar:
        st.header("🎛️ Controls")
        
        status = "<span class='status-online'>🟢 Online</span>" if st.session_state.agent_running else "<span class='status-offline'>🔴 Offline</span>"
        st.markdown(f"**Status:** {status}", unsafe_allow_html=True)
        st.divider()

        user_intent = st.text_input("🗣️ What should the agent do?", placeholder="e.g. 'Click the submit button'")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Execute", use_container_width=True, type="primary"):
                if user_intent:
                    st.session_state.agent_running = True
                else:
                    st.warning("Please enter a command.")
        with col2:
            if st.button("🛑 Stop", use_container_width=True):
                st.session_state.agent_running = False
                log_ui("User halted execution loop.")

        st.divider()
        st.subheader("🧠 Semantic Memory")
        st.metric(label="Learned Rules", value=len(memory.rules))
        if st.button("Clear Memory"):
            reflection._save_memory([])
            memory._load_memory() # Refresh FAISS
            log_ui("Cleared all memory rules.")

    # -- Main Content --
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Agent's Vision (Set-of-Mark Overlay)")
        image_placeholder = st.empty()
        if st.session_state.latest_image:
            image_placeholder.image(st.session_state.latest_image, use_container_width=True)
        else:
            image_placeholder.info("Agent is idle. Awaiting command.")

    with col_right:
        st.subheader("Action Logs")
        log_container = st.container(height=500)
        with log_container:
            for log in st.session_state.logs:
                st.code(log, language=None)

    # --- Agentic Execution Logic Loop ---
    if st.session_state.agent_running and user_intent:
        log_ui(f"USER: '{user_intent}'")
        
        # 1. Capture screen & apply Set-of-Mark
        log_ui("Capturing screen and routing to OpenCV Set-of-Mark...")
        raw_b64, file_path = capture_screen(save_debug=True)
        
        img_b64, coord_map = apply_set_of_mark(file_path)
        st.session_state.latest_image = file_path 
        
        # 2. Get Rules via FAISS
        rules = memory.query_top_k(user_intent, k=5)
        if rules:
            log_ui(f"Semantic RAG retrieved {len(rules)} relevant rules.")
        
        # 3. Vision API
        log_ui("Requesting Action Plan [Array] from Gemini 2.5 Flash...")
        action_plan = vision.analyze_screen(img_b64, coord_map, user_intent, rules)
        
        if not action_plan:
            log_ui("ERROR: Gemini failed to generate a plan.")
            st.session_state.agent_running = False
            st.rerun()

        log_ui(f"Plan received with {len(action_plan)} steps. Engaging PyAutoGUI Executor.")
        
        first_step = action_plan[0] if action_plan else None
        if first_step and "x" in first_step:
            target_img_path = draw_target_circle(file_path, first_step['x'], first_step['y'])
            st.session_state.latest_image = target_img_path
        
        # 4. Execute Native
        success = execute_plan(action_plan)
        
        if success:
            log_ui("SUCCESS: Action executed safely.")
        else:
            log_ui("FAIL: Execution encountered an error.")
        st.session_state.agent_running = False
        st.rerun()


if __name__ == "__main__":
    main()
