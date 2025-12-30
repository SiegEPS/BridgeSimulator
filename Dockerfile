FROM python:3.11-slim-bookworm

# Install build tools, multi-threading support, AND git
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy your app files
COPY . .

# 1. Remove the empty placeholder folder Render might have created
# 2. Clone the redeal repo manually into that spot
# 3. Enter the dds folder and compile it
RUN rm -rf redeal && \
    git clone --recursive https://github.com/overthebridge/redeal.git && \
    cd redeal/dds/src && \
    make

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set the path so Python finds the newly cloned redeal
ENV PYTHONPATH=".:./redeal"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]