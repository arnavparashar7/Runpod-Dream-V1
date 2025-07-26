FROM runpod/worker-comfyui:5.2.0-base

#python req
RUN apt-get update && apt-get install -y git git-lfs && git lfs install

#Florence requiremment Transformers
RUN pip install transformers==4.38.2

# --- Install Custom Nodes ---
RUN comfy-node-install comfyui-kjnodes x-flux-comfyui comfyui_controlnet_aux comfyui-florence2 

#Text Enccoders
RUN comfy model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip --filename clip_l.safetensors
RUN comfy model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors --relative-path models/clip --filename t5xxl_fp8_e4m3fn_scaled.safetensors

# UNET/Diffusion Model
RUN comfy model download --url https://huggingface.co/Comfy-Org/flux1-kontext-dev_ComfyUI/resolve/main/split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors --relative-path models/diffusion_models --filename flux1-dev-kontext_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-dev-fp8.safetensors --relative-path models/diffusion_models --filename flux1-dev-fp8.safetensors
RUN wget https://huggingface.co/GraydientPlatformAPI/flux-inpainting-faster/resolve/main/flux-fill-inpainting-fp8-yogotatara.safetensors -O /comfyui/models/diffusion_models/flux1-fill-dev.safetensors

# VAE
RUN comfy model download --url https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors --relative-path models/vae --filename ae.safetensors

# Flux ControlNet Model
RUN comfy model download --url https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors --relative-path models/xlabs/controlnets --filename flux-depth-controlnet-v3.safetensors
RUN comfy model download --url https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors --relative-path models/controlnets --filename flux-depth-controlnet-v3.safetensors
# Depth ControlNet Model
RUN comfy model download --url "https://huggingface.co/spaces/depth-anything/Depth-Anything-V2"  --relative-path models/controlnet --filename depth_anything_v2_vitl.pth
# /comfyui/models/controlnet/depth-anything

#florence LLM
RUN huggingface-cli download microsoft/Florence-2-large-ft --local-dir /comfyui/models/LLM/Florence-2-large-ft

# --- Setup worker application files ---

COPY workflows/ ./workflows/
COPY process_handler.py process_handler.py .
COPY handler.py .

