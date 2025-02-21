FROM python:3.9

# Install dependencies and packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the content to the image
COPY api/ .

# Command to run
CMD ["python","app.py"]