"""
SightNav — Vision Utilities (Set-of-Mark Grounding)
===================================================
Applies OpenCV edge/contour detection to the screenshot,
drawing a red bounding box with a unique ID over every 
clickable UI element.

This forces Gemini to just pick an ID instead of guessing
absolute pixel coordinates.
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from src.utils.logger import Logger

def apply_set_of_mark(image_path: str) -> tuple[str, dict]:
    """
    Reads an image, detects UI elements, draws numbered red boxes,
    and returns a base64 encoded string of the NEW image along with
    a dictionary mapping IDs to (x, y) coordinates.
    
    Returns:
        tuple: (base64_encoded_image: str, coordinate_map: dict)
               where coordinate_map is {1: (x, y), 2: (x, y), ...}
    """
    Logger.info("Applying Set-of-Mark (SoM) bounding boxes to screenshot...")
    
    # 1. Load image via OpenCV
    img = cv2.imread(image_path)
    if img is None:
        Logger.error(f"OpenCV could not read image at {image_path}")
        return "", {}
        
    original = img.copy()
    
    # 2. Convert to grayscale & edge detect 
    # (Tuning Canny thresholds for UI elements)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Morphological closing to join text/button parts
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # 3. Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    coordinate_map = {}
    box_id = 1
    
    # Define colors
    box_color = (0, 0, 255)      # Red in BGR
    text_color = (255, 255, 255) # White
    bg_color = (0, 0, 255)       # Red background for text
    
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        
        # Filter out tiny noise and massive background wrappers
        if w > 20 and h > 10 and w < (img.shape[1] * 0.8) and h < (img.shape[0] * 0.8):
            
            # Calculate center point
            center_x = x + (w // 2)
            center_y = y + (h // 2)
            
            coordinate_map[box_id] = (center_x, center_y)
            
            # Draw the bounding box
            cv2.rectangle(img, (x, y), (x+w, y+h), box_color, 2)
            
            # Draw the ID label background and text at top-left of box
            label = f"[{box_id}]"
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x, y - text_h - 4), (x + text_w, y), bg_color, -1)
            cv2.putText(img, label, (x, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
            
            box_id += 1
            
    Logger.success(f"SoM generated {box_id - 1} interactive targets.")
    
    # 4. Save and return Base64
    # We blend it slightly with the original so the UI isn't totally covered in red lines
    alpha = 0.8
    blended = cv2.addWeighted(img, alpha, original, 1 - alpha, 0)
    
    # Convert back to PIL for easy base64 encoding without saving to disk
    blended_rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(blended_rgb)
    
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return img_str, coordinate_map

def draw_target_circle(image_path: str, x: int, y: int, radius: int = 30) -> str:
    """
    Draws a highly visible neon circle on the image at (x, y) to show the user 
    exactly where the agent clicked inside the Streamlit Dashboard.
    Returns path to the modified image.
    """
    img = cv2.imread(image_path)
    if img is not None:
        cv2.circle(img, (x, y), radius, (0, 255, 255), 4) # Yellow circle
        cv2.circle(img, (x, y), radius + 4, (0, 0, 255), 2)  # Red outer ring
        cv2.circle(img, (x, y), radius - 4, (0, 0, 0), 2)    # Black inner ring
        cv2.circle(img, (x, y), 2, (0, 0, 255), -1)          # Red dot in center
        
        target_path = image_path.replace(".png", "_target.png")
        cv2.imwrite(target_path, img)
        return target_path
    return image_path
