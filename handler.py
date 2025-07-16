import json
import requests
import base64
import time
import runpod

COMFY_HOST = "127.0.0.1:8188"

def image_url_to_base64(url):
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

def upload_images(images):
    for image in images:
        name = image["name"]
        data_uri = image["image"]
        
        if "," in data_uri:
            base64_data = data_uri.split(",", 1)[1]
        else:
            base64_data = data_uri

        blob = base64.b64decode(base64_data)

        files = {
            "image": (name, blob, "image/png"),
            "overwrite": (None, "true")
        }

        response = requests.post(f"http://{COMFY_HOST}/upload/image", files=files, timeout=30)
        response.raise_for_status()

def queue_workflow(workflow, client_id):
    payload = {"prompt": workflow, "client_id": client_id}
    response = requests.post(
        f"http://{COMFY_HOST}/prompt",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def get_history(prompt_id):
    response = requests.get(f"http://{COMFY_HOST}/history/{prompt_id}", timeout=30)
    response.raise_for_status()
    return response.json()

def get_image_data(filename, subfolder, image_type):
    params = {
        "filename": filename,
        "subfolder": subfolder,
        "type": image_type
    }
    response = requests.get(f"http://{COMFY_HOST}/view", params=params, timeout=60)
    response.raise_for_status()
    return response.content

def handler(job):
    job_input = job.get("input")
    if not job_input:
        raise ValueError("Missing 'input' in job payload.")

    workflow_input = job_input.get("workflow")
    if not workflow_input:
        raise ValueError("Missing 'workflow' in job input.")

    workflow_type = workflow_input.get("type")
    if not workflow_type:
        raise ValueError("Missing 'workflow.type' in input.")

    prompt_input_text = workflow_input.get("prompt_input")
    if prompt_input_text is None:
        raise ValueError("Missing 'prompt_input' in workflow.")

    if "images" not in job_input or not isinstance(job_input["images"], list):
        raise ValueError("'images' must be a list of image URLs or objects.")

    # Load workflow template from disk
    with open(f"workflows/{workflow_type}.json", "r") as file:
        workflow = json.load(file)

    # Validate required nodes
    if "43" not in workflow or "inputs" not in workflow["43"]:
        raise ValueError("Workflow template is missing node 43 or its inputs.")
    if "59" not in workflow or "inputs" not in workflow["59"]:
        raise ValueError("Workflow template is missing node 59 or its inputs.")

    # Patch the workflow
    workflow["43"]["inputs"]["text"] = prompt_input_text
    workflow["59"]["inputs"]["image"] = "input_image.png"

    # Prepare images
    images = []
    for idx, item in enumerate(job_input["images"]):
        if isinstance(item, str):
            # Just a URL string
            images.append({
                "name": f"input_image_{idx}.png",
                "image": image_url_to_base64(item)
            })
        elif isinstance(item, dict) and "image" in item and "name" in item:
            # Client provided an object
            if item["image"].startswith("http"):
                item_copy = item.copy()
                item_copy["image"] = image_url_to_base64(item["image"])
                images.append(item_copy)
            else:
                images.append(item)
        else:
            raise ValueError(f"Invalid image format at index {idx}. Must be string or object with 'name' and 'image'.")

    # Upload images to ComfyUI
    upload_images(images)

    # Queue the workflow
    client_id = "handler-client-1234"
    queue_result = queue_workflow(workflow, client_id)
    prompt_id = queue_result.get("prompt_id")

    if not prompt_id:
        return {"error": "Failed to queue workflow: missing prompt_id"}

    # Poll for result
    max_attempts = 30
    delay_seconds = 5

    for attempt in range(max_attempts):
        history = get_history(prompt_id)
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs")
            if outputs:
                results = []

                for node_id, node_data in outputs.items():
                    if "images" in node_data:
                        for img in node_data["images"]:
                            filename = img["filename"]
                            subfolder = img.get("subfolder", "")
                            img_type = img.get("type", "output")
                            image_bytes = get_image_data(filename, subfolder, img_type)
                            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                            results.append({
                                "filename": filename,
                                "data": image_b64
                            })
                return {
                    "status": "completed",
                    "prompt_id": prompt_id,
                    "images": results
                }

        time.sleep(delay_seconds)

    return {
        "status": "timeout",
        "prompt_id": prompt_id,
        "message": "Workflow did not complete in time."
    }

if __name__ == "__main__":
    print("worker-comfyui - Starting handler...")
    runpod.serverless.start({"handler": handler})
