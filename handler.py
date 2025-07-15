import runpod
import requests
import base64
import json
import uuid
import os
from cloudflare import Cloudflare

# ---------------------
# Cloudflare Setup
# ---------------------
CF_API_TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]
CF_ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
cf_client = Cloudflare(api_token=CF_API_TOKEN)

# ---------------------
# Runpod Endpoint
# ---------------------
runpod.api_key = os.environ.get("RUNPOD_API_KEY")
endpoint = runpod.Endpoint(os.environ.get("ENDPOINT_ID"))

# ---------------------
# Workflow Injection Config
# ---------------------
WORKFLOW_CONFIG = {
    "fill": {
        "filename": "fill.json",
        "prompts": [{"node": 43, "input_index": 0}],
        "image": {"node": 57, "input_index": 0}
    },
    "Redesign": {
        "filename": "Redesign.json",
        "prompts": [
            {"node": 63, "input_index": 0},
            {"node": 15, "input_index": 0, "fixed_value": "remove all the furniture like sofas, tables, plants, lights, fireplace, paintings, curtains and carpet"}
        ],
        "image": {"node": 14, "input_index": 0}
    }
}

# ---------------------
# Helpers
# ---------------------
def image_url_to_base64(image_url):
    resp = requests.get(image_url, timeout=10)
    return base64.b64encode(resp.content).decode("utf-8")

def upload_to_cloudflare(image_bytes):
    direct_upload = cf_client.images.v2.direct_uploads.create(account_id=CF_ACCOUNT_ID)
    upload_url = direct_upload.upload_url
    result = requests.post(upload_url, files={"file": image_bytes}, timeout=30)
    result.raise_for_status()
    return direct_upload.id

# ---------------------
# Handler
# ---------------------
def handler(job):
    data = job["input"]
    workflow_key = data.get("workflow", "fill")
    config = WORKFLOW_CONFIG.get(workflow_key)

    if not config:
        return {"error": f"Invalid workflow key: {workflow_key}"}

    # Load workflow from JSON
    with open(f"workflows/{config['filename']}", "r") as file:
        workflow = json.load(file)

    # Inject prompts
    prompt_text = (data.get("prompt") or [""])[0]

    for prompt_cfg in config["prompts"]:
        node_id = str(prompt_cfg["node"])
        if "fixed_value" in prompt_cfg:
            workflow[node_id]["inputs"]["text"] = prompt_cfg["fixed_value"]
        else:
            workflow[node_id]["inputs"]["text"] = prompt_text


    # Prepare unique filename
    unique_id = f"{uuid.uuid4().hex}.png"

    # Inject image node
    image_node_id = str(config["image"]["node"])
    image_input_idx = config["image"]["input_index"]
    workflow[image_node_id]["inputs"]["image"] = unique_id

    # Get base64 image
    image_b64 = image_url_to_base64(data["image_url"])

    # Prepare payload for Runpod
    runpod_input = {
        "workflow": workflow,
        "images": [{"name": unique_id, "image": image_b64}]
    }

    # Call Comfy
    result = endpoint.run_sync(runpod_input)

    # Grab resulting images
    images_out = result.get("images", [])
    output_urls = []

    for img in images_out:
        if img["type"] == "base64":
            img_bytes = base64.b64decode(img["data"])
            try:
                # Try Cloudflare upload
                cf_id = upload_to_cloudflare(img_bytes)
                output_urls.append({"filename": img["filename"], "cloudflare_id": cf_id})
            except Exception:
                # Fallback to base64 if upload fails
                output_urls.append({"filename": img["filename"], "base64": img["data"]})

    return {"images": output_urls}


# Start the Runpod serverless handler
runpod.serverless.start({"handler": handler})
