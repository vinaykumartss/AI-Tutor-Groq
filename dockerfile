FROM public.ecr.aws/docker/library/python:3.10
WORKDIR /app
COPY . .

# Upgrade pip and install the required packages
RUN pip3 install --upgrade pip
RUN pip3  install -r requirements.txt
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/insightxdev_com.key", "--ssl-certfile", "/app/insightxdev.com.key"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/meeting.appmatric.com.key", "--ssl-certfile", "/app/meeting.appmatric.com.crt"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
