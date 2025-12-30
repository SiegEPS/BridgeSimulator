FROM python:3.11-slim-bookworm

# Install build tools, multi-threading support, and git
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 1. Clone redeal (recursive pulls the dds submodule)
# 2. Navigate to the dds/src directory
# 3. Copy the Linux-specific Makefile from its actual location: os/linux/Makefile
# 4. Run make
RUN rm -rf redeal && \
    git clone --depth 1 --recursive https://github.com/anntzer/redeal.git && \
    pip install ./redeal && \
    cd redeal/dds/src && \
    cp os/linux/Makefile . && \
    make

# Install app requirements
RUN pip install --no-cache-dir -r requirements.txt

# Tell the app where to find the compiled .so file
# We add both the src and the redeal folders to the path
ENV LD_LIBRARY_PATH="/app/redeal/dds/src:${LD_LIBRARY_PATH}"
ENV PYTHONPATH=".:./redeal"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]