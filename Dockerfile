FROM python:3.11-slim-bookworm

# Install build tools and libgomp1 (required for the solver to run)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# 1. Clone redeal
# 2. Install it using pip (this handles the C++ compilation automatically)
RUN rm -rf redeal && \
    git clone --depth 1 --recursive https://github.com/anntzer/redeal.git && \
    pip install ./redeal

# Install your app's requirements
RUN pip install --no-cache-dir -r requirements.txt

# This is the "Magic" step: 
# We find the compiled .so file that pip just created and make sure its 
# directory is in the system's library path so 'ctypes' can find it.
ENV PYTHONPATH="."
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/redeal:${LD_LIBRARY_PATH}"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]