# sadaya-polban-odoo (eProcurement System)

## Overview

**Sadaya Polban** (Sistem Andalan PengaDAyan dan LaYAnan Jasa) is a comprehensive E-Procurement Information System developed specifically for Politeknik Negeri Bandung (Polban). The system is designed to digitalize, automate, and integrate the entire procurement cycle for goods and services from beginning to end through a single gateway.

### System Architecture

Built on top of the robust **Odoo ERP** infrastructure using **Docker** and **CI/CD** technologies, Sadaya Polban ensures scalability and reliability. The system is tailored to meet Polban's requirements as a State Service Agency (BLU) with specific budget thresholds and procurement regulations.

### Core Modules

The system comprises five interconnected main modules:

1. **SIDAPET** (Vendor Registration System) - The main gateway and database system where all vendors register and manage their company profiles
2. **Quotation** (Proposal Module) - Initial interaction bridge between Polban admin and vendors for bidding
3. **Tender** (Open Selection) - Handles large-value procurement packages (above Rp200 Million) with strict workflow management
4. **Direct Procurement** - Manages procurement packages below the budget threshold with simplified processes
5. **SIBELA** (Direct Purchase System) - Fast and efficient operational transaction module for quick purchases

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 1.29 or higher)
- **Git** (for cloning the repository)

### Installation Guide

#### Windows
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Docker Compose is included with Docker Desktop

#### Linux
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose
```

#### macOS
- Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/incognieto/sadaya-polban-odoo
cd sadaya-polban-odoo
```

### 2. Project Structure

The project contains the following structure:

```
sadaya-polban-odoo/
├── docker-compose.yml       # Docker Compose configuration file
├── custom_addons/           # Custom Odoo modules and addons
└── README.md
```

### 3. Starting the Application

#### Step 1: Build and Start Docker Services

Navigate to the project directory and run:

```bash
docker-compose up -d
```

This command will:
- Pull the required Docker images (Odoo 19.0 and PostgreSQL 15)
- Create and start two services:
  - **web**: Odoo application server
  - **db**: PostgreSQL database server
- Mount custom addons from the `./custom_addons` folder
- Create persistent volumes for data storage

#### Step 2: Wait for Services to Initialize

The services may take 1-3 minutes to fully initialize. You can check the status with:

```bash
docker-compose ps
```

Or view the logs:

```bash
docker-compose logs -f web
```

### 4. Accessing Odoo Web Interface

Once the services are running, open your web browser and navigate to:

```
http://localhost:8069
```

#### Initial Setup

1. The first time you access Odoo, you will be prompted to create a new database
2. Enter a database name (e.g., `sadaya_polban`)
3. Create an admin user with a secure password
4. Odoo will initialize with the default configuration

#### Custom Addons

Custom addons located in the `./custom_addons` folder are automatically mounted in the Docker container at `/mnt/extra-addons`. These will be available in Odoo's module list once the system is initialized.

To install custom modules:
1. Go to **Apps** in the Odoo menu
2. Update the apps list (click the refresh icon)
3. Search for and install your custom modules

## Docker Services Configuration

### Services

**Web Service (Odoo 19.0)**
- Port: `8069`
- Database connection: `db:5432`
- Admin user: `odoo`
- Admin password: `odoo`

**Database Service (PostgreSQL 15)**
- Database name: `postgres`
- Username: `odoo`
- Password: `odoo`
- Internal port: `5432` (not exposed externally)

### Volumes

- `odoo-web-data`: Stores Odoo application data
- `odoo-db-data`: Stores PostgreSQL database files

## Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f web        # Odoo logs
docker-compose logs -f db         # Database logs
```

### Restart Services
```bash
docker-compose restart
```

### Remove All Data (⚠️ Warning: Destructive)
```bash
docker-compose down -v
```

This will remove all containers, networks, and volumes, permanently deleting all data.

## Troubleshooting

### Services Won't Start
- Check Docker is running: `docker ps`
- Review logs: `docker-compose logs`
- Ensure ports 8069 are not in use: `netstat -an | grep 8069`

### Cannot Access Odoo Web Interface
- Wait 2-3 minutes for services to fully initialize
- Verify services are running: `docker-compose ps`
- Check firewall settings and ensure port 8069 is accessible

### Database Connection Issues
- Verify the `db` service is running: `docker-compose logs db`
- Check environment variables in `docker-compose.yml`
- Ensure PostgreSQL credentials match between services

### Custom Addons Not Appearing
- Verify addons are in the `./custom_addons` folder
- Restart the web service: `docker-compose restart web`
- Refresh the apps list in Odoo

## System Requirements

- **Minimum RAM**: 2GB
- **Minimum Storage**: 5GB
- **Recommended RAM**: 4GB or more
- **Recommended Storage**: 20GB or more

## Support & Documentation

For more information about the system modules and features, refer to:
- `Deskripsi Sistem.txt` - Detailed system description in Indonesian

## License

This project is developed for Politeknik Negeri Bandung (Polban).

---

**Last Updated**: April 2026
