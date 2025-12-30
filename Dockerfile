FROM python:3.11-slim-bookworm

# We still need build-essential and libgomp1 so pip has a compiler to use
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy your project files
COPY . .

# 1. Clean and Clone redeal (since Render isn't pulling the submodules)
# 2. Use pip to install the redeal folder. 
#    The '.' at the end tells pip to install the package from the current directory.
RUN rm -rf redeal && \
    git clone --depth 1 --recursive https://github.com/anntzer/redeal.git && \
    pip install ./redeal

# Install the rest of your app's requirements
RUN pip install --no-cache-dir -r requirements.txt

# Set the path
ENV PYTHONPATH=".:./redeal"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]