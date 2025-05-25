FROM python:3.10

# Set workdir
WORKDIR /app

# Copy backend code
COPY backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Terraform (HashiCorp official instructions)
RUN apt-get update && apt-get install -y gnupg software-properties-common curl unzip \
  && curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/hashicorp.list \
  && apt-get update && apt-get install -y terraform \
  && terraform -install-autocomplete

# Expose Flask port
EXPOSE 5000

# Run the backend
CMD ["python", "backend.py"]

