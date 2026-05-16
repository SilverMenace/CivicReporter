from roboflow import Roboflow
import os
import sys

# --- Credentials for Pothole Model (Account 1) ---
POTHOLE_API_KEY = "x136LxX4RJdNn1liIin8" 
POTHOLE_WORKSPACE_ID = "myproject-rf0c1" 
POTHOLE_PROJECT_ID = "garbage-pothole-lvpsk"   
POTHOLE_VERSION = 1

# --- Credentials for Garbage Model (Account 2) ---

GARBAGE_API_KEY = "RvFfwyH8LCMHevMGqgiV"
GARBAGE_WORKSPACE_ID = "shadow-ynt6s"
GARBAGE_PROJECT_ID = "garbage-yzrfd-qbb3m"
GARBAGE_VERSION = 1 
# --- Initialize Both Roboflow Models from their respective accounts ---
try:
    print("Initializing Roboflow and loading hosted models from separate accounts...")
    
    # Initialize and load the pothole model using its own API key
    pothole_rf = Roboflow(api_key=POTHOLE_API_KEY)
    pothole_project = pothole_rf.workspace(POTHOLE_WORKSPACE_ID).project(POTHOLE_PROJECT_ID)
    pothole_model = pothole_project.version(POTHOLE_VERSION).model
    print("- Pothole model loaded successfully.")

    # Initialize and load the garbage model using its own API key
    garbage_rf = Roboflow(api_key=GARBAGE_API_KEY)
    garbage_project = garbage_rf.workspace(GARBAGE_WORKSPACE_ID).project(GARBAGE_PROJECT_ID)
    garbage_model = garbage_project.version(GARBAGE_VERSION).model
    print("- Garbage model loaded successfully.")

except Exception as e:
    print(f"Error initializing Roboflow models: {e}")
    print("Please double-check that all API keys, workspace IDs, and project IDs are correct.")
    sys.exit()


def analyze_image(image_file_path: str):
    """
    Analyzes an image using BOTH the pothole and garbage hosted Roboflow models 
    and aggregates their results into a single list.
    """
    print(f"Analyzing {image_file_path} with all AI models...")
    aggregated_results = []
    
    try:
        # --- 1. Run Pothole Detection via API ---
        print(" -> Checking for potholes...")
        pothole_prediction = pothole_model.predict(image_file_path, confidence=40, overlap=30).json()
        
        for pred in pothole_prediction['predictions']:
            aggregated_results.append({
                "class": pred['class'],
                "confidence": pred['confidence']
            })

        # --- 2. Run Garbage Detection via API ---
        print(" -> Checking for garbage...")
        garbage_prediction = garbage_model.predict(image_file_path, confidence=40, overlap=30).json()

        for pred in garbage_prediction['predictions']:
            aggregated_results.append({
                "class": "garbage",
                "confidence": pred['confidence']
            })
        
        print(f"API analysis complete. Found {len(aggregated_results)} total detections.")
        
    except Exception as e:
        print(f"An error occurred during API prediction: {e}")
        return [] # Return empty list if any API call fails
            
    return aggregated_results