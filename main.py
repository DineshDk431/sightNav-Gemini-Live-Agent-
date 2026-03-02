import os
from dotenv import load_dotenv

from src.utils.logger import Logger
from src.tools.screen_capture import capture_screen
from src.tools.executor import execute_plan
from src.agents.vision_agent import VisionAgent
from src.agents.reflection_agent import ReflectionAgent
from src.agents.audio_agent import AudioAgent
from src.utils.vision_utils import apply_set_of_mark

def main():
    # 1. Environment Init
    load_dotenv()
    Logger.banner()
    Logger.info("Booting SightNav Orchestrator...")

    # 2. Subsystem Init
    try:
        audio = AudioAgent()
        vision = VisionAgent()
        reflection = ReflectionAgent()
        Logger.success("All Intelligent Agents initialized.")
    except Exception as e:
        Logger.error(f"Failed to initialize agents: {e}")
        return

    # 3. Main Loop
    Logger.divider("System Ready")
    audio.speak("SightNav is ready. What would you like me to do?")

    while True:
        # Step 1 (Perceive): Get Intent
        intent = audio.listen()
        
        if intent.lower() in ['exit', 'quit', 'stop']:
            Logger.info("Shutting down SightNav...")
            audio.speak("Goodbye!")
            break
            
        if not intent:
            continue

        # Step 2: Current state capture
        _, before_path = capture_screen(save_debug=True)
        if not before_path:
            audio.speak("Error capturing the screen. Retrying...")
            continue
            
        img_b64, coord_map = apply_set_of_mark(before_path)

        # Step 3 (Plan & Route): Get rules and analyze
        rules = reflection.get_rules()
        if rules:
            Logger.memory(f"Loaded {len(rules)} rules.")
            
        action_plan = vision.analyze_screen(img_b64, coord_map, intent, rules)
        
        if not action_plan or "action" not in action_plan[0]:
            Logger.warn("Vision Agent could not generate a valid plan.")
            audio.speak("I couldn't figure out how to do that.")
            continue

        # Step 4 (Act): Execute
        success = execute_plan(action_plan)
        
        if not success:
            audio.speak("I encountered an error executing the action.")
            continue

        # Step 5 (Verify): Check result
        # Small delay to let the UI update
        import time
        time.sleep(1.0) 
        
        _, after_path = capture_screen(save_debug=True)
        
        # Step 6: User feedback loop (Reflection trigger)
        audio.speak("Action executed. Did that do what you wanted? (yes/no)")
        feedback = audio.listen().lower()
        
        if feedback in ['no', 'n', 'wrong', 'fail']:
            audio.speak("I apologize. Let's reflect on what went wrong. Why did it fail?")
            complaint = audio.listen()
            
            # Trigger Reflection
            reflection.reflect_on_failure(
                before_img_path=before_path,
                after_img_path=after_path,
                attempted_action=action_plan,
                user_complaint=complaint
            )
            audio.speak("Got it. I've updated my memory so I won't do that next time.")
            
        else:
            audio.speak("Great. What's next?")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
