FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 1. Clone redeal
# 2. Use 'find' to confirm where the actual solver source code ended up
# 3. Install redeal
RUN rm -rf redeal && \
    git clone --recursive https://github.com/anntzer/redeal.git && \
    find redeal -name "doubledummy.c" && \
    pip install ./redeal

# 4. Find the compiled .so file and link it to 'dds.so'
# We use a broader find search here to be safe
RUN SO_FILE=$(find /usr/local/lib/python3.11/site-packages/redeal -name "*.so" | head -n 1) && \
    if [ -n "$SO_FILE" ]; then ln -s $SO_FILE /usr/local/lib/python3.11/site-packages/redeal/dds.so; fi

RUN pip install --no-cache-dir -r requirements.txt

ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/redeal:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="."

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]