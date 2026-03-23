FROM python:3.11-slim-bookworm
WORKDIR /app
COPY requirements.txt .

# Bypass SSL inspection for secure corporate networks
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY main.py .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
