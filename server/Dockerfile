
# Install libmagic
RUN apt-get update && apt-get install -y libmagic1

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]