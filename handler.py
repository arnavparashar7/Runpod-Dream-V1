import runpod
import os
import base64
import requests
from io import BytesIO

# Constants for Cloudflare
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

COMFY_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")

def handler(job):
    job_input = job["input"]
    workflow_type = job_input["workflow"].get("type")

    # Load the selected workflow
    with open(f"workflows/{workflow_type}.json", "r") as f:
        workflow = json.load(f)

    # Inject input values depending on workflow type
    match workflow_type:
        case "fill":
            workflow["43"]["inputs"]["text"] = job_input["workflow"]["prompt_input"]
            workflow["59"]["inputs"]["image"] = "input_image.png"

        case "redesign":
            workflow["63"]["inputs"]["text"] = job_input["workflow"]["prompt_input"]
            workflow["14"]["inputs"]["image"] = "input_image.png"
            workflow["28"]["inputs"]["ControlNetStrength"] = job_input["workflow"].get("ControlNetStrength", 0.8)
            workflow["27"]["inputs"]["denoise_strength"] = job_input["workflow"].get("denoise_strength", 0.8)

        case _:
            return {"error": f"Unsupported workflow type: {workflow_type}"}

    # Get the image URL and convert to base64
    image_url = job_input.get("image_url")
    if not image_url:
        return {"error": "Missing image_url in input."}

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_b64 = base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        return {"error": f"Failed to download or encode image: {str(e)}"}

    # Upload image to ComfyUI
    files = {
        "image": ("input_image.png", base64.b64decode(image_b64), "image/png"),
        "overwrite": (None, "true")
    }
    try:
        up = requests.post(f"{COMFY_URL}/upload/image", files=files)
        up.raise_for_status()
    except Exception as e:
        return {"error": f"Image upload to ComfyUI failed: {str(e)}"}

    # Queue the workflow
    try:
        queue_payload = {
            "prompt": workflow,
            "client_id": "handler-client-1234"
        }
        queued = requests.post(f"{COMFY_URL}/prompt", json=queue_payload)
        queued.raise_for_status()
        prompt_id = queued.json().get("prompt_id")
    except Exception as e:
        return {"error": f"Failed to queue workflow: {str(e)}"}

    if not prompt_id:
        return {"error": "No prompt_id received from ComfyUI."}

    # Poll for result (5 sec * 30 times = up to 2.5 min)
    for _ in range(30):
        try:
            result = requests.get(f"{COMFY_URL}/history/{prompt_id}").json()
            if prompt_id in result:
                output_data = []
                for node_id, node in result[prompt_id].get("outputs", {}).items():
                    for img in node.get("images", []):
                        view_params = {
                            "filename": img["filename"],
                            "subfolder": img.get("subfolder", ""),
                            "type": img.get("type", "output")
                        }
                        img_bytes = requests.get(f"{COMFY_URL}/view", params=view_params).content

                        # Upload to Cloudflare
                        if CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN:
                            headers = {
                                "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"
                            }
                            upload_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1"
                            files = {"file": (img["filename"], BytesIO(img_bytes), "image/png")}

                            cf_response = requests.post(upload_url, headers=headers, files=files)
                            cf_response.raise_for_status()
                            image_url = cf_response.json()["result"]["variants"][0]

                            output_data.append({
                                "filename": img["filename"],
                                "url": image_url
                            })
                        else:
                            # Fallback to base64
                            output_data.append({
                                "filename": img["filename"],
                                "data": base64.b64encode(img_bytes).decode("utf-8")
                            })

                return {
                    "status": "completed",
                    "prompt_id": prompt_id,
                    "images": output_data
                }
        except Exception:
            pass

        time.sleep(5)

    return {
        "status": "timeout",
        "prompt_id": prompt_id,
        "message": "Workflow did not complete in time."
    }

if __name__ == "__main__":
    print("worker-comfyui - Starting handler...")
    runpod.serverless.start({"handler": handler})
