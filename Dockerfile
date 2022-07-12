FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg gcc make vim
WORKDIR /MilkDiscordBot
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py ./
COPY ./Controller ./Controller
COPY ./Common ./Common

CMD ["python", "Milk.py"]