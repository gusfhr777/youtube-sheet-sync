FROM python:3.12-slim

# work directory
WORKDIR /app

# copy requirements.txt
COPY requirements.txt .

# install packages
RUN pip install --no-cache-dir -r requirements.txt

# copy all codes
COPY . .

# execute command
CMD ["python", "main.py"]
