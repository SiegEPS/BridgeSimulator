FROM python:3.11-slim-bookworm

# Install build tools, multi-threading support (libgomp1), and git
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 1. Full recursive clone to ensure submodules (DDS) are 100% present
# 2. Verification: check for a core C file to ensure the submodule isn't empty
# 3. Build and install redeal via pip
RUN rm -rf redeal && \
    git clone --recursive https://github.com/anntzer/redeal.git && \
    ls -la redeal/dds/src/doubledummy.c && \
    pip install ./redeal

# 4. Create a symbolic link so redeal's ctypes loader finds the library 
#    under the expected 'dds.so' name regardless of the complex pip-generated name.
RUN SO_FILE=$(find /usr/local/lib/python3.11/site-packages/redeal -name "*.so" | head -n 1) && \
    ln -s $SO_FILE /usr/local/lib/python3.11/site-packages/redeal/dds.so || true

# Install your app's requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set Environment Variables
# LD_LIBRARY_PATH helps the system find the C++ shared object
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/redeal:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="."

# Expose Render's default port and run
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]