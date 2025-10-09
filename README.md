# Mortgage Refinery

A Python-based service that monitors mortgage interest rates and determines when refinancing would result in meaningful savings.

## Prerequisites

Before running the service, ensure you have the following installed and configured:

- **Docker** & **Docker Compose** - used to build and run the containerized service
- **SMTP credentials** - required for sending email alerts

## Usage

Start by cloning this repo.

```bash
git clone https://github.com/philiporlando/mortgage_refinery.git
cd mortgage_refinery
```

Create a `config.yaml` and `.env` file, and populate them with the necessary config values.

Then build and start the service:

```bash
docker compose up --build -d
```

The container will start in detached mode and begin running the monitoring service according to the provided configuration.
