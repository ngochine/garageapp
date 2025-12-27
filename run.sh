#!/bin/bash

if [ -f "venv/Scripts/activate" ]; then
    echo "Đã tồn tại môi trường ảo"
else
    echo "Tạo môi trường ảo"
    python -m venv venv
fi

source venv/Scripts/activate

pip install -r requirements.txt