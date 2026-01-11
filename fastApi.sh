#!/bin/bash
echo "execute Trade python"
source ./venv/bin/activate
uvicorn main:app --port 8000 --reload
