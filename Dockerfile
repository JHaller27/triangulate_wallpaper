FROM python:3.9

EXPOSE 8000

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
