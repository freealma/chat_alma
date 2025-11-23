FROM python:3.11

WORKDIR /alma

COPY . .

RUN pip install -e .

CMD ["alma"]