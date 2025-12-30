FROM python:3.11-slim-bookworm

# Install build tools, libgomp (required for DDS), and git
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy your local project files
COPY . .

# 1. Clean up and clone the primary redeal repo
# 2. Enter the DDS src directory
# 3. Create a 'Makefile' from the Linux template provided by the library
# 4. Compile the shared library (.so)
RUN rm -rf redeal && \
    git clone --depth 1 --recursive https://github.com/anntzer/redeal.git && \
    cd redeal/dds/src && \
    cp Makefiles/Makefile_Linux_shared Makefile && \
    make

# Install your Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set paths so Python can find the redeal folder and its compiled C++ solver
ENV PYTHONPATH=".:./redeal"

# Expose the port Render expects (10000)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]