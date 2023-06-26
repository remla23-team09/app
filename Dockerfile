FROM python:3.9-slim

WORKDIR /app
COPY ./.git ./.git
RUN apt update
RUN apt install git -y
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY static ./static
COPY templates ./templates
COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]