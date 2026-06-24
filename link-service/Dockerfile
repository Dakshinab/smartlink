# Start from official Python 3.12 slim image
# 'slim' means smaller size - only what we need
FROM python:3.12-slim

# Set working directory inside the container
# All commands below run from this folder
WORKDIR /app

# Copy requirements first (before copying code)
# Why? Docker caches layers - if requirements don't change,
# it won't reinstall packages every time. Saves time!
COPY requirements.txt .

# Install packages inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of our code
COPY . .

# Tell Docker our app runs on port 5001
EXPOSE 5001

# Command to start the app
CMD ["python", "run.py"]