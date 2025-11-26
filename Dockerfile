FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Cài hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

# Dùng Python 3.10
RUN python3.10 -m pip install --upgrade pip

# Cài PyTorch GPU
RUN python3.10 -m pip install torch==2.6.0+cu124 torchaudio==2.6.0+cu124 torchvision==0.21.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Xóa PyTorch khỏi requirements.txt và cài các package còn lại
RUN  python3.10 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python3.10", "manage.py", "runserver", "0.0.0.0:8000"]
