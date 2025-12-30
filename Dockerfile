FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all files
COPY . .

# Check if redeal exists; if not, the build should fail here 
# with a clear message so we know Render didn't pull the submodule.
RUN ls -la redeal/dds/src || (echo "ERROR: redeal folder is empty. Check your Git Submodule settings on Render." && exit 1)

# Build the solver
RUN cd redeal/dds/src && make

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=".:./redeal"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]s