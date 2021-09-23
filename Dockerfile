FROM alpine:latest

COPY . /root

WORKDIR /root
RUN apk add python3 cmd:pip3
RUN pip3 install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]