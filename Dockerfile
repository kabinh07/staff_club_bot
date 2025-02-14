FROM 3.11.11-alpine3.20

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ['python3', 'main.py']