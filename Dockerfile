FROM --platform=linux/amd64 python:3.11.4-slim

ENV TZ=Asia/Seoul

WORKDIR /app
COPY . .

RUN pip install -r ./requirements.txt && \
    pip install --no-cache-dir -e .

CMD ["python", "-m", "pregen.main"]
