FROM python:alpine
RUN apk update ; apk add py-pip
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]