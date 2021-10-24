#1 
FROM python:3.7

#3 
COPY src/ /app
WORKDIR /app

#2
RUN pip install -y -r requirements.txt

#4
ENV PORT 8080

#5
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
# CMD python app.py