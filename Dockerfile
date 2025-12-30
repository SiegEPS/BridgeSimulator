FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# 1. Use the correct primary URL: https://github.com/anntzer/redeal
# 2. Use --depth 1 to minimize network issues
# 3. Compile the solver
RUN rm -rf redeal && \
    git clone --depth 1 --recursive https://github.com/anntzer/redeal.git && \
    cd redeal/dds/src && \
    make

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=".:./redeal"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]