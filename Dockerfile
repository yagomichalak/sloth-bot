# Start from a base image
FROM python:3.9-slim

# Install git
RUN apt-get update && apt-get install -y git && apt-get clean

# Copy all files from the current directory to the container
COPY . .

RUN pip install --upgrade pip

RUN pip install git+https://github.com/Rapptz/discord-ext-menus

RUN pip install py-cord==2.6.0

RUN pip install -r requirements.txt

# Command to run your application
CMD ["python", "main.py"]