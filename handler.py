import json
import requests
import base64
import runpod
import json
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

        case "redesign":
            workflow["63"]["inputs"]["text"] = job_input["workflow"]["prompt_input"]
            workflow["14"]["inputs"]["image"] = "input_image.png"
            workflow["28"]["inputs"]["ControlNetStrength"] = job_input["workflow"].get("ControlNetStrength", 0.8)
            workflow["27"]["inputs"]["denoise_strength"] = job_input["workflow"].get("desnoise_strength", 0.8)
            
        case _:
            return {"error": f"Unknown workflow type: {workflow_type}"}


    image_url = job_input["image_url"]
    
    runpod_input = {
        "workflow": workflow,
        "images": [
          {
            "name": "image_input.png",
            "image": image_url_to_base64(image_url),
          }
        ]
      }
    return runpod_input

        # Run the job on the remote endpoint
    result = endpoint.run_sync(runpod_input)
    
    # --- Decode and Upload the Result to Cloudflare ---

    # 1. Get the base64 data and decode it back to binary bytes
    image_base64 = result["images"][0]["data"]
    image_bytes = base64.b64decode(image_base64)

    # 2. Prepare the request for the Cloudflare API
    api_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    files = {"file": (f"{unique_id}.png", image_bytes, "image/png")}

    # 3. Post the image to Cloudflare
    response = requests.post(api_url, headers=headers, files=files)
    response.raise_for_status()

    # 4. Extract the public URL and return it
    upload_result = response.json()
    public_url = upload_result["result"]["variants"][0]

    return public_url

runpod.serverless.start({"handler": handler})
