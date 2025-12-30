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
# 1. Clone redeal
# 2. Build extension in-place to generate libdds.so
# 3. Install package
# 4. Copy libdds.so manually to site-packages (bypassing wheel exclusion issues)
RUN rm -rf redeal && \
    git clone --recursive https://github.com/anntzer/redeal.git && \
    cd redeal && \
    python3 setup.py build_ext --inplace && \
    pip install . && \
    # Find site-packages and copy libdds.so
    SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    echo "Copying libdds.so to $SITE_PACKAGES/redeal/" && \
    cp redeal/libdds.so "$SITE_PACKAGES/redeal/" && \
    # Set correct permissions
    chmod 755 "$SITE_PACKAGES/redeal/libdds.so" && \
    # Verify installation works
    python3 -c "from redeal import dds; dds._check_dll('VerifyBuild'); print('DDS Loaded Successfully')" && \
    cd .. && rm -rf redeal

RUN pip install --no-cache-dir -r requirements.txt

ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/redeal:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="."

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]