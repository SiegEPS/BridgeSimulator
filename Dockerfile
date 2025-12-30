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
    # Patch setup.py to ensures libdds.so is included in the wheel package
    sed -i "s/packages=\[\"redeal\"\],/packages=[\"redeal\"], package_data={'redeal': ['*.so']},/" redeal/setup.py && \
    pip install ./redeal

# 4. Check for .so file and ensure it is named 'libdds.so' as expected by dds.py
RUN SO_FILE=$(find /usr/local/lib/python3.11/site-packages/redeal -name "*.so" | head -n 1) && \
    if [ -z "$SO_FILE" ]; then \
        echo "Error: No .so file found in installed redeal package."; \
        exit 1; \
    fi && \
    echo "Found SO_FILE: $SO_FILE" && \
    # Create symlink to libdds.so if the found file has a different name
    if [ "$(basename "$SO_FILE")" != "libdds.so" ]; then \
        ln -s "$SO_FILE" "$(dirname "$SO_FILE")/libdds.so"; \
    fi

RUN pip install --no-cache-dir -r requirements.txt

ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/redeal:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="."

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]