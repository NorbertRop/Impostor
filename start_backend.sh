#!/bin/bash

cd backend
echo "Starting FastAPI backend on http://localhost:8000"
uvicorn main:app --reload

