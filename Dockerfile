FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt update && apt upgrade -y && apt install -y \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    nginx \
    git \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add LLVM 10 repository for Ubuntu focal (for llvm-10)
RUN wget https://apt.llvm.org/llvm-snapshot.gpg.key && \
    apt-key add llvm-snapshot.gpg.key && \
    echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-10 main" > /etc/apt/sources.list.d/llvm.list && \
    apt update && \
    apt install -y llvm-10 llvm-10-dev && \
    rm llvm-snapshot.gpg.key

# Clone Amber repo
RUN git clone https://github.com/roshanshibu/amber.git /amber

# Copy from local for dev
# COPY . /amber

# Set working directory to Scripts folder
WORKDIR /amber

# Set execute permission on fpcalc
RUN chmod +x /amber/bin/fpcalc

# Set up Python virtual environment and install dependencies
RUN python3 -m venv AMBER_ENV && \
    . AMBER_ENV/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Replace nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start server
CMD service nginx start && \
    . AMBER_ENV/bin/activate && \
    python server.py
