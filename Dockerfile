# Use a Python 3.11 base image
FROM python:3.11-slim-bookworm

# Install system dependencies for C++ compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the entire project
# (Render will have already pulled your submodules into these folders)
COPY . .

# Build the DDS library inside the submodule folder
# Note: We just run 'make', no 'git' commands needed here.
RUN cd redeal/dds/src && make

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the PYTHONPATH so Python can find redeal and its solver
ENV PYTHONPATH=".:./redeal"

# Final command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]