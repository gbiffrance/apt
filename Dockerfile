FROM python:3.8-alpine

WORKDIR /usr/src/app

RUN mkdir -p /usr/data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./apt.py" ]
