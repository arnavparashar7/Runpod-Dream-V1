import json
import requests
import base64
import runpod
import os

# --- Environment Configuration ---
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")

# --- Initialize RunPod ---
runpod.api_key = RUNPOD_API_KEY
endpoint = runpod.Endpoint(ENDPOINT_ID)

def image_url_to_base64(url):
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")

def handler(job):
    job_input = job["input"]
    workflow_type = job_input["workflow"]["type"]

    with open(f"workflows/{workflow_type}.json", "r") as file:
        workflow = json.load(file)

    match workflow_type:
        case "fill":
            workflow["43"]["inputs"]["text"] = job_input["workflow"]["prompt_input"]
            workflow["59"]["inputs"]["image"] = "input_image.png"

        case "fill_hires":
            workflow["43"]["inputs"]["text"] = job_input["workflow"]["prompt_input"]
            workflow["59"]["inputs"]["image"] = "input_image.png"

        case "redesign_cn":
            workflow["74"]["inputs"]["value"] = job_input["workflow"]["prompt_input"]
            workflow["14"]["inputs"]["image"] = "input_image.png"
            workflow["28"]["inputs"]["strength"] = job_input["workflow"].get("ControlNetStrength", 0.8)
            workflow["27"]["inputs"]["image_to_image_strength"] = job_input["workflow"].get("image_to_image_strength", 0)
            workflow["27"]["inputs"]["denoise_strength"] = job_input["workflow"].get("desnoise_strength", 0.8)
            
        case _:
            return {"error": f"Unknown workflow type: {workflow_type}"}


    image_url = job_input["image_url"]
    
    runpod_input = {
        "workflow": workflow,
        "images": [
          {
            "name": "input_image.png",
            "image": image_url_to_base64(image_url),
          }
        ]
      }
    return runpod_input
