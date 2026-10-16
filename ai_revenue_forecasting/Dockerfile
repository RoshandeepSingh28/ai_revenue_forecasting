FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data artifacts logs
EXPOSE 5000
CMD ["sh", "-c", "python scripts/generate_data.py && python scripts/train_model.py && python app.py"]
