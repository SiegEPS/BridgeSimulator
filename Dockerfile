# Use a Python 3.11 base image
FROM python:3.11-slim-bookworm

# Install system dependencies for C++ compilation and multi-threading
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the entire project (including submodules)
COPY . .

# Initialize and build the DDS library inside the submodule
RUN git submodule update --init --recursive && \
    cd redeal/dds/src && \
    make && \
    cd ../../../

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the PYTHONPATH so Python can find redeal and its solver
ENV PYTHONPATH=".:./redeal"

# Final command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]