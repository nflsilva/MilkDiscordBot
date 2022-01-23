FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y ffmpeg gcc make vim

WORKDIR /MilkDiscordBot


COPY *.py ./
COPY ./Controller ./Controller
COPY .env .
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "App.py"]