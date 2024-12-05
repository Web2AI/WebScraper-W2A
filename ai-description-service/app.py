import logging
from io import BytesIO

import requests
import torch
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel
from transformers import BlipForConditionalGeneration, BlipProcessor

app = FastAPI()
logger = logging.getLogger()


class ImageRequest(BaseModel):
    url: str


model_name = "Salesforce/blip-image-captioning-base"
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained(model_name)
model = BlipForConditionalGeneration.from_pretrained(model_name).to(device)


@app.post("/generate-description/")
async def generate_description(image: ImageRequest):
    try:
        response = requests.get(image.url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to fetch image from URL"
            )
        image = Image.open(BytesIO(response.content)).convert("RGB")

        # Preprocess image and generate caption
        inputs = processor(images=image, return_tensors="pt").to(device)
        output_ids = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(output_ids[0], skip_special_tokens=True)
        logger.info(f"Generated caption: {caption}")
        return {"description": caption}

    except Exception as e:
        print(f"Error generating description: {e}")
        raise HTTPException(status_code=500, detail=str(e))
