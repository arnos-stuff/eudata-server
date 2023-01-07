FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/root/.local/bin:${PATH}"
# Install dependencies
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the project files
COPY . /app

# Set the working directory
WORKDIR /app

# Install the dependencies
RUN poetry install


EXPOSE 8000
# Run the application
CMD ["srv" "prod" "--host" "0.0.0.0" "--port" "8000"]
