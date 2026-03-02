import os
import time
import streamlit as st
from dotenv import load_dotenv
from src.utils.logger import Logger
from src.tools.screen_capture import capture_screen
from src.tools.executor import execute_plan
from src.agents.vision_agent import VisionAgent
from src.agents.reflection_agent import ReflectionAgent
from src.agents.safety_agent import SafetyAgent
from src.agents.audio_agent import AudioAgent
from src.utils.vision_utils import apply_set_of_mark, draw_target_circle
from src.utils.memory_manager import MemoryManager

st.set_page_config(
    page_title="SightNav AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .status-online { color: #00FF00; font-weight: bold; }
    .status-offline { color: #FF0000; font-weight: bold; }
    .risk-high { color: #FF0000; font-weight: bold; }
    .risk-medium { color: #FFA500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'agent_running' not in st.session_state:
        st.session_state.agent_running = False
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'latest_image' not in st.session_state:
        st.session_state.latest_image = None
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
def log_ui(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {msg}")
    Logger.info(msg)

@st.cache_resource
def init_system():
    load_dotenv()
    log_ui("Initializing Advanced Cognitive Subsystems...")
    vision = VisionAgent()
    reflection = ReflectionAgent()
    safety = SafetyAgent()
    memory = MemoryManager()
    audio = AudioAgent()
    log_ui("Gatekeeper, Tri-Reasoning, and Subsystems Online.")
    return vision, reflection, safety, memory, audio

# --- Main UI Build ---
def main():
    init_session_state()
    st.title("👁️ SightNav Agent Control Center V3")
    st.caption("Powered by Gemini 2.5 Flash, OpenCV Set-of-Mark, and Tri-Reasoning Validation.")

    try:
        vision, reflection, safety, memory, audio = init_system()
        if not st.session_state.system_initialized:
            st.session_state.system_initialized = True
    except Exception as e:
        st.error(f"Failed to boot logic: {e}")
        st.stop()

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
            if st.button("🎙️ Voice Cmd", use_container_width=True):
                st.session_state.agent_running = True
                with st.spinner("🎤 Listening..."):
                    intent_from_mic = audio.listen()
                    
                if intent_from_mic == "ERROR_MIC_FAIL":
                    st.error("Microphone hardware disconnected or denied permissions by Windows. Please type instead.")
                    st.session_state.agent_running = False
                elif intent_from_mic:
                    user_intent = intent_from_mic
                else:
                    st.session_state.agent_running = False
                    
        if st.button("🛑 Halt System", use_container_width=True):
            st.session_state.agent_running = False
            log_ui("User halted execution loop.")

        st.divider()
        st.subheader("🧠 Semantic Memory")
        st.metric(label="Learned Rules", value=len(memory.rules))
        if st.button("Clear Memory"):
            reflection._save_memory([])
            memory._load_memory()
            log_ui("Cleared all memory rules.")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Agent's Vision (SoM Bounding Boxes)")
        image_placeholder = st.empty()
        if st.session_state.latest_image:
            image_placeholder.image(st.session_state.latest_image, use_container_width=True)
        else:
            image_placeholder.info("Agent is idle. Awaiting command.")

    with col_right:
        st.subheader("Action Logs (Reasoning Monologue)")
        log_container = st.container(height=600)
        with log_container:
            for log in st.session_state.logs:
                if "❌ Blocked" in log:
                    st.markdown(f"<span class='risk-high'>`{log}`</span>", unsafe_allow_html=True)
                elif "HITL" in log or "[Critic]" in log:
                    st.markdown(f"<span class='risk-medium'>`{log}`</span>", unsafe_allow_html=True)
                else:
                    st.code(log, language=None)

    # --- Agentic Execution Logic Loop ---

    if st.session_state.agent_running and user_intent:
        log_ui(f"USER: '{user_intent}'")
        # Force a UI refresh immediately so the sidebar Status shows "🟢 Online"
        st.session_state.agent_running = True
        
        with st.spinner("🧠 🤖 Agent is Analyzing & Reasoning..."):
            log_ui("Evaluating intent via Safety Gatekeeper...")
            safety_check = safety.check_intent(user_intent)
            
            if not safety_check.get("is_safe", False):
                risk = safety_check.get("risk_level", "unknown")
                reason = safety_check.get("violation_reason", "Action deemed unsafe.")
                
                if risk == "high":
                    log_ui(f"❌ Blocked (HIGH RISK): {reason}")
                    audio.speak("I cannot do that. The action violates security protocols.")
                    st.session_state.agent_running = False
                    st.rerun()
                    
                elif risk == "medium":
                    log_ui(f"⚠️ Security Hold (HITL): {reason}")
                    audio.speak("This action requires confirmation. Please say 'Confirm' to proceed, or 'Cancel'.")
                    confirmation = audio.listen()
                    if not confirmation or "confirm" not in confirmation.lower() and "yes" not in confirmation.lower():
                        log_ui("❌ User cancelled or failed to confirm HITL action.")
                        audio.speak("Action cancelled.")
                        st.session_state.agent_running = False
                        st.rerun()
                    else:
                        log_ui("✅ User Authorized Medium Risk Action.")
            
            # 1. Perception
            log_ui("Capturing screen and routing to OpenCV Set-of-Mark...")
            raw_b64, file_path = capture_screen(save_debug=True)
            img_b64, coord_map = apply_set_of_mark(file_path)
            
            st.session_state.latest_image = file_path 
            
            # 2. Memory RAG
            rules = memory.query_top_k(user_intent, k=5)
            
            # 3. Vision Action Plan
            log_ui("Engaging Vision Agent for Execution Plan...")
            action_plan = vision.analyze_screen(img_b64, coord_map, user_intent, rules)
            
            if not action_plan:
                log_ui("ERROR: Vision Agent failed to generate a plan.")
                audio.speak("I'm confused by the screen and decided it's safer to stop.")
                st.session_state.agent_running = False
                st.rerun()

            log_ui(f"Execution Plan Generated: {len(action_plan)} steps via native Windows API.")
            
            first_step = action_plan[0] if action_plan else None
            if first_step and "x" in first_step:
                target_img_path = draw_target_circle(file_path, first_step['x'], first_step['y'])
                st.session_state.latest_image = target_img_path
            
            # 4. Action
            success = execute_plan(action_plan)
            if success:
                log_ui("SUCCESS: Array Routine executed safely.")
                audio.speak("Action complete.")
            else:
                log_ui("FAIL: Execution encountered OS errors.")
                audio.speak("Something went wrong with the mouse automation.")
                
        # Turn off running state after spinner completes
        st.session_state.agent_running = False
        st.rerun()


if __name__ == "__main__":
    main()
