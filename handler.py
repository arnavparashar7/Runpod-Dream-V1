import json
import requests
import base64
import runpod


def image_url_to_base64(url):
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")

def handler(job):
    job_input = job["input"]
    workflow_type = job_input["workflow"]

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

runpod.serverless.start({"handler": handler})
