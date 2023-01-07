FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Install dependencies
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the project files
COPY . /app

# Set the working directory
WORKDIR /app

# Install the dependencies
RUN poetry shell
RUN poetry install

# Run the application
CMD ["srv" "prod" "--host" "0.0.0.0" "--port" "8080"]