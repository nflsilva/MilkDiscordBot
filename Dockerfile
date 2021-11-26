FROM python:3.9

RUN apt-get update && \
    apt-get install -y ffmpeg

WORKDIR /MilkDiscordBot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .
COPY ./Module ./Module

CMD ["python", "main.py"]