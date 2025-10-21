FROM python:3.12-bookworm

WORKDIR /app

# Install system dependencies for compiling Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir flask pandas scikit-learn numpy==1.26.4 surprise psutil

EXPOSE 8000

CMD ["python3", "app.py"]
