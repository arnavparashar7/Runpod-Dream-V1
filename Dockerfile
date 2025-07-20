FROM runpod/worker-comfyui:5.2.0-base

# --- Install Custom Nodes ---
RUN comfy-node-install comfyui-kjnodes x-flux-comfyui comfyui_controlnet_aux comfyui-florence2


RUN comfy model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip --filename clip_l.safetensors
RUN comfy model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors --relative-path models/clip --filename t5xxl_fp8_e4m3fn_scaled.safetensors

# UNET/Diffusion Model
RUN comfy model download --url https://huggingface.co/Comfy-Org/flux1-kontext-dev_ComfyUI/resolve/main/split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors --relative-path models/diffusion_models --filename flux1-dev-kontext_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-dev-fp8.safetensors --relative-path models/diffusion_models --filename flux1-dev-fp8.safetensors

# VAE
RUN comfy model download --url https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors --relative-path models/vae --filename ae.safetensors

# Flux ControlNet Model
RUN comfy model download --url https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors --relative-path models/controlnet --filename flux-depth-controlnet-v3.safetensors

#florence Model download
# LLM
#RUN huggingface-cli download microsoft/Florence-2-large-ft --local-dir /comfyui/models/LLM/Florence-2-large-ft

# --- Setup worker application files ---
# Set the working directory for your application code
# This will be /workspace/worker, where your handler and workflows are.

# Create the src directory
# RUN mkdir -p /workspace/worker/src


# ADD src/start.sh /workspace/worker/start.sh
# COPY handler.py .
# RUN chmod +x /workspace/worker/start.sh

# COPY workflows/ /workspace/worker/workflows/
# COPY input/ /comfyui/input/
