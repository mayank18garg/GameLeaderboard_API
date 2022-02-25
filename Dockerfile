FROM python:latest
WORKDIR /application
COPY . /application
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD [ "python3", "app.py" ]