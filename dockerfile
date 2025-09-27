FROM public.ecr.aws/docker/library/python:3.10

WORKDIR /app
COPY requirements.txt .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .

# Run a syntax check during build
RUN python -m compileall .

# Optional: Run tests or linting (uncomment if needed)
# RUN pip install pytest flake8 && pytest --maxfail=1 --disable-warnings -q && flake8 .
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/insightxdev_com.key", "--ssl-certfile", "/app/insightxdev.com.key"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/meeting.appmatric.com.key", "--ssl-certfile", "/app/meeting.appmatric.com.crt"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
