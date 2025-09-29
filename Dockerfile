FROM python:3.13-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias del sistema para mysqlclient (temporales para no inflar la imagen)
RUN apk update \
    && apk add --no-cache mariadb-connector-c-dev \
    && apk add --virtual .build-deps gcc musl-dev mariadb-dev pkg-config \
    && pip install --default-timeout=100 --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copiar el resto del código
COPY . .

EXPOSE 5000

CMD [ "python", "run.py" ]
#CMD sh -c "gunicorn --bind 0.0.0.0:8081 --workers 4 --forwarded-allow-ips=*  wsgi:app"