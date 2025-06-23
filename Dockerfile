FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
COPY . /app
CMD ["pytest", "tests"]
