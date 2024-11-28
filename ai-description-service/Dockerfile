FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; \
              processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); \
              model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]