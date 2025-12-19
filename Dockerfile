FROM python3:latest

# Set the working directory in the container
WORKDIR /app
# Copy the requirements file into the container at /app
COPY requirements.txt /app/
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code into the container
COPY . /app/
# Expose the port the app runs on
EXPOSE 8000
# Set the environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=fastTransfer.fastTransfer.settings
# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]