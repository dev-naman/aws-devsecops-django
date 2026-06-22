# # Use the official Python image as a base image
# FROM python:3.12.1-bullseye

# # Set environment variables for Python
# # ENV PYTHONUNBUFFERED=1
# # ENV PYTHONDONTWRITEBYTECODE=1

# # Set the working directory
# WORKDIR /app

# # Copy and install dependencies
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the Django project
# COPY . /app/

# # Expose port and define the run command
# EXPOSE 8000

# ENTRYPOINT ["/bin/bash","./entrypoint.sh"]

# #CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m django

RUN chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "drf.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
