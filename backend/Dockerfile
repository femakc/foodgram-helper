FROM python:3.7

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir

COPY . .

WORKDIR /app/foodgram

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]  
