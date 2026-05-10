FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . /app/src

EXPOSE 7860

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
