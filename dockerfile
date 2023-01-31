FROM python:3.8-slim-buster

WORKDIR /fetch

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
ENV PYTHONPATH "${PYTHONPATH}:/src"

ENTRYPOINT ["python3", "./src/main.py"]