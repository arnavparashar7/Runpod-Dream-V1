import json
import requests
import base64
import runpod
import os
import random

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
            workflow["14"]["inputs"]["guidance"] = job_input["workflow"].get("FluxGuidance", 2.5)
            workflow["6"]["inputs"]["seed"] = job_input["workflow"].get("seed", random.randint(0, 1014642931094358))
            workflow["6"]["inputs"]["steps"] = job_input["workflow"].get("steps", 20)
            workflow["6"]["inputs"]["cfg"] = job_input["workflow"].get("cfg", 1)
            workflow["6"]["inputs"]["sampler_name"] = job_input["workflow"].get("sampler", "euler")
            workflow["6"]["inputs"]["scheduler"] = job_input["workflow"].get("scheduler", "normal")
            workflow["6"]["inputs"]["denoise"] = job_input["workflow"].get("denoise", 1)

        case "fill_hires":
            workflow["43"]["inputs"]["text"] = job_input["workflow"]["prompt_input"]
            workflow["59"]["inputs"]["image"] = "input_image.png"
            workflow["14"]["inputs"]["guidance"] = job_input["workflow"].get("FluxGuidance", 2.5)
            workflow["76"]["inputs"]["text"] = job_input["workflow"].get("hi_prompt", "a furnished room")
            workflow["62"]["inputs"]["guidance"] = job_input["workflow"].get("hi_FluxGuidance", 3.5)
            workflow["75"]["inputs"]["seed"] = job_input["workflow"].get("hi_seed", random.randint(0, 1014642931094358))
            workflow["75"]["inputs"]["steps"] = job_input["workflow"].get("hi_steps", 20)
            workflow["75"]["inputs"]["cfg"] = job_input["workflow"].get("hi_cfg", 1)
            workflow["75"]["inputs"]["sampler_name"] = job_input["workflow"].get("hi_sampler", "euler")
            workflow["75"]["inputs"]["scheduler"] = job_input["workflow"].get("hi_scheduler", "beta")
            workflow["75"]["inputs"]["denoise"] = job_input["workflow"].get("hi_denoise", 0.4)
            workflow["74"]["inputs"]["method"] = job_input["workflow"].get("hi_color_match_method", "reinhard") #mkl, hm, reinhard, mvgd, hm-mvgd-hm, hm-mkl-hm
            workflow["6"]["inputs"]["seed"] = job_input["workflow"].get("seed", random.randint(0, 1014642931094358))
            workflow["6"]["inputs"]["steps"] = job_input["workflow"].get("steps", 20)
            workflow["6"]["inputs"]["cfg"] = job_input["workflow"].get("cfg", 1)
            workflow["6"]["inputs"]["sampler_name"] = job_input["workflow"].get("sampler", "euler")
            workflow["6"]["inputs"]["scheduler"] = job_input["workflow"].get("scheduler", "normal")
            workflow["6"]["inputs"]["denoise"] = job_input["workflow"].get("denoise", 1)

        case "redesign_cn":
            workflow["74"]["inputs"]["value"] = job_input["workflow"]["prompt_input"]
            workflow["14"]["inputs"]["image"] = "input_image.png"
            workflow["28"]["inputs"]["strength"] = job_input["workflow"].get("ControlNetStrength", 0.8)
            workflow["27"]["inputs"]["noise_seed"] = job_input["workflow"].get("seed", random.randint(0, 1014642931094358))
            workflow["27"]["inputs"]["steps"] = job_input["workflow"].get("steps", 25)
            workflow["27"]["inputs"]["timestep_to_start_cfg"] = job_input["workflow"].get("cfg", 1)
            workflow["27"]["inputs"]["true_gs"] = job_input["workflow"].get("true_gs", 3.5)
            workflow["27"]["inputs"]["image_to_image_strength"] = job_input["workflow"].get("image_to_image_strength", 0)
            workflow["27"]["inputs"]["denoise_strength"] = job_input["workflow"].get("desnoise_strength", 1)

        case "redesign_mask":
            workflow["5"]["inputs"]["guidance"] = job_input["workflow"].get("FluxGuidance", 30)
            workflow["10"]["inputs"]["text"] = job_input["workflow"].get("prompt_input")
            workflow["28"]["inputs"]["text_input"] = job_input["workflow"].get("MaskPrompt1", "furniture")
            workflow["29"]["inputs"]["text_input"] = job_input["workflow"].get("MaskPrompt2", "furniture")
            workflow["28"]["inputs"]["task"] = job_input["workflow"].get("MaskingTask", "caption_to_phrase_grounding")
            workflow["29"]["inputs"]["task"] = job_input["workflow"].get("MaskingTask", "caption_to_phrase_grounding")
            workflow["20"]["inputs"]["image"] = "input_image.png"
            workflow["12"]["inputs"]["strength"] = job_input["workflow"].get("ControlNetStrength", 1)
            workflow["12"]["inputs"]["start_percent"] = job_input["workflow"].get("StartPercent", 0)
            workflow["12"]["inputs"]["end_percent"] = job_input["workflow"].get("EndPercent", 0.8)
            workflow["2"]["inputs"]["seed"] = job_input["workflow"].get("seed", random.randint(0, 1014642931094358))
            workflow["2"]["inputs"]["steps"] = job_input["workflow"].get("steps", 25)
            workflow["2"]["inputs"]["cfg"] = job_input["workflow"].get("cfg", 1)
            workflow["2"]["inputs"]["sampler_name"] = job_input["workflow"].get("sampler", "euler")
            workflow["2"]["inputs"]["scheduler"] = job_input["workflow"].get("scheduler", "normal")
            workflow["2"]["inputs"]["denoise"] = job_input["workflow"].get("denoise", 1)

        case "redesign_mask_hires":
            workflow["5"]["inputs"]["guidance"] = job_input["workflow"].get("FluxGuidance", 30)
            workflow["10"]["inputs"]["text"] = job_input["workflow"].get("prompt_input")
            workflow["28"]["inputs"]["text_input"] = job_input["workflow"].get("MaskPrompt1", "furniture")
            workflow["29"]["inputs"]["text_input"] = job_input["workflow"].get("MaskPrompt2", "furniture")
            workflow["28"]["inputs"]["task"] = job_input["workflow"].get("MaskingTask", "caption_to_phrase_grounding")
            workflow["29"]["inputs"]["task"] = job_input["workflow"].get("MaskingTask", "caption_to_phrase_grounding")
            workflow["20"]["inputs"]["image"] = "input_image.png"
            workflow["12"]["inputs"]["strength"] = job_input["workflow"].get("ControlNetStrength", 1)
            workflow["12"]["inputs"]["start_percent"] = job_input["workflow"].get("StartPercent", 0)
            workflow["12"]["inputs"]["end_percent"] = job_input["workflow"].get("EndPercent", 0.8)
            workflow["2"]["inputs"]["seed"] = job_input["workflow"].get("seed", random.randint(0, 1014642931094358))
            workflow["2"]["inputs"]["steps"] = job_input["workflow"].get("steps", 25)
            workflow["2"]["inputs"]["cfg"] = job_input["workflow"].get("cfg", 1)
            workflow["2"]["inputs"]["sampler_name"] = job_input["workflow"].get("sampler", "euler")
            workflow["2"]["inputs"]["scheduler"] = job_input["workflow"].get("scheduler", "normal")
            workflow["2"]["inputs"]["denoise"] = job_input["workflow"].get("denoise", 1)
            workflow["51"]["inputs"]["text"] = job_input["workflow"].get("hi_prompt", "a furnished room")
            workflow["43"]["inputs"]["guidance"] = job_input["workflow"].get("hi_FluxGuidance", 3.5)
            workflow["50"]["inputs"]["seed"] = job_input["workflow"].get("hi_seed", random.randint(0, 1014642931094358))
            workflow["50"]["inputs"]["steps"] = job_input["workflow"].get("hi_steps", 20)
            workflow["50"]["inputs"]["cfg"] = job_input["workflow"].get("hi_cfg", 1)
            workflow["50"]["inputs"]["sampler_name"] = job_input["workflow"].get("hi_sampler", "euler")
            workflow["50"]["inputs"]["scheduler"] = job_input["workflow"].get("hi_scheduler", "beta")
            workflow["50"]["inputs"]["denoise"] = job_input["workflow"].get("hi_denoise", 0.4)
            workflow["59"]["inputs"]["method"] = job_input["workflow"].get("hi_color_match_method", "reinhard") #mkl, hm, reinhard, mvgd, hm-mvgd-hm, hm-mkl-hm

            
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
