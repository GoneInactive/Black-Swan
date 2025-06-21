# TradeByte Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Considerations](#security-considerations)
8. [Performance Optimization](#performance-optimization)
9. [Backup and Recovery](#backup-and-recovery)

## Overview

This guide covers deploying TradeByte in various environments, from local development to production cloud deployments. TradeByte is designed to be flexible and can run on different platforms with minimal configuration changes.

## Local Development Setup

### Prerequisites

```bash
# System requirements
- Python 3.10+
- Rust 1.70+
- Git
- pip
- maturin

# Operating systems
- Windows 10/11
- macOS 10.15+
- Ubuntu 20.04+ / CentOS 8+
```

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/GoneInactive/TradeByte.git
cd TradeByte
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Set Up Rust Environment
```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install maturin
pip install maturin

# Build Rust components
cd rust_client
maturin develop
cd ..
```

#### 4. Configuration Setup
```bash
# Create configuration directory
mkdir -p config

# Create configuration file
cat > config/config.yaml << EOF
kraken:
  api_key: "${KRAKEN_API_KEY}"
  api_secret: "${KRAKEN_API_SECRET}"
  sandbox: true  # Set to false for production

trading:
  default_pair: "BTC/USD"
  max_position_size: 1000
  min_order_size: 10
  max_order_size: 1000

risk_management:
  max_daily_loss: 100
  max_position_risk: 0.02
  stop_loss_pct: 0.05

logging:
  level: "INFO"
  file: "logs/tradebyte.log"
  max_size: "10MB"
  backup_count: 5

websocket:
  ping_interval: 20
  ping_timeout: 10
  reconnect_delay: 5
EOF
```

#### 5. Environment Variables
```bash
# Set environment variables
export KRAKEN_API_KEY="your_api_key_here"
export KRAKEN_API_SECRET="your_api_secret_here"

# For Windows PowerShell
$env:KRAKEN_API_KEY="your_api_key_here"
$env:KRAKEN_API_SECRET="your_api_secret_here"
```

#### 6. Test Installation
```bash
# Run tests
python tests/test_rust_client.py
python tests/test_api.py

# Test market maker strategy
python src/apps/strategies/market_maker.py
```

## Production Deployment

### System Requirements

```bash
# Minimum system requirements
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 100Mbps stable connection
- OS: Ubuntu 20.04 LTS or CentOS 8
```

### Production Setup

#### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y build-essential curl git
sudo apt install -y supervisor nginx

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

#### 2. Application Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash tradebyte
sudo usermod -aG sudo tradebyte

# Switch to application user
sudo su - tradebyte

# Clone repository
git clone https://github.com/GoneInactive/TradeByte.git
cd TradeByte

# Set up Python environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build Rust components
cd rust_client
maturin develop
cd ..
```

#### 3. Configuration
```bash
# Create production configuration
cat > config/config.yaml << EOF
kraken:
  api_key: "${KRAKEN_API_KEY}"
  api_secret: "${KRAKEN_API_SECRET}"
  sandbox: false

trading:
  default_pair: "BTC/USD"
  max_position_size: 5000
  min_order_size: 50
  max_order_size: 5000

risk_management:
  max_daily_loss: 500
  max_position_risk: 0.01
  stop_loss_pct: 0.03

logging:
  level: "INFO"
  file: "/var/log/tradebyte/tradebyte.log"
  max_size: "100MB"
  backup_count: 10

websocket:
  ping_interval: 20
  ping_timeout: 10
  reconnect_delay: 5

monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 30
EOF
```

#### 4. Systemd Service Setup
```bash
# Create systemd service file
sudo tee /etc/systemd/system/tradebyte.service << EOF
[Unit]
Description=TradeByte Trading Platform
After=network.target

[Service]
Type=simple
User=tradebyte
Group=tradebyte
WorkingDirectory=/home/tradebyte/TradeByte
Environment=PATH=/home/tradebyte/TradeByte/venv/bin
Environment=KRAKEN_API_KEY=your_api_key_here
Environment=KRAKEN_API_SECRET=your_api_secret_here
ExecStart=/home/tradebyte/TradeByte/venv/bin/python src/apps/strategies/market_maker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tradebyte
sudo systemctl start tradebyte

# Check status
sudo systemctl status tradebyte
```

#### 5. Logging Setup
```bash
# Create log directory
sudo mkdir -p /var/log/tradebyte
sudo chown tradebyte:tradebyte /var/log/tradebyte

# Configure logrotate
sudo tee /etc/logrotate.d/tradebyte << EOF
/var/log/tradebyte/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 tradebyte tradebyte
    postrotate
        systemctl reload tradebyte
    endscript
}
EOF
```

## Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install maturin
RUN pip install maturin

# Copy Rust source and build
COPY rust_client/ ./rust_client/
WORKDIR /app/rust_client
RUN maturin build --release
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data config

# Create non-root user
RUN useradd -m -s /bin/bash tradebyte && \
    chown -R tradebyte:tradebyte /app
USER tradebyte

# Expose ports
EXPOSE 5000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Start command
CMD ["python", "src/apps/strategies/market_maker.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  tradebyte:
    build: .
    container_name: tradebyte
    restart: unless-stopped
    environment:
      - KRAKEN_API_KEY=${KRAKEN_API_KEY}
      - KRAKEN_API_SECRET=${KRAKEN_API_SECRET}
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "5000:5000"
      - "9090:9090"
    networks:
      - tradebyte-network

  nginx:
    image: nginx:alpine
    container_name: tradebyte-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - tradebyte
    networks:
      - tradebyte-network

  prometheus:
    image: prom/prometheus:latest
    container_name: tradebyte-prometheus
    restart: unless-stopped
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - tradebyte-network

  grafana:
    image: grafana/grafana:latest
    container_name: tradebyte-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - tradebyte-network

volumes:
  prometheus_data:
  grafana_data:

networks:
  tradebyte-network:
    driver: bridge
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream tradebyte {
        server tradebyte:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://tradebyte;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /metrics {
            proxy_pass http://tradebyte:9090;
        }
    }
}
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Setup
```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://user-data.sh
```

#### 2. User Data Script
```bash
#!/bin/bash
# user-data.sh

# Update system
yum update -y

# Install Python 3.10
yum install -y python3.10 python3.10-pip

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env

# Clone TradeByte
cd /home/ec2-user
git clone https://github.com/GoneInactive/TradeByte.git
cd TradeByte

# Set up Python environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build Rust components
cd rust_client
maturin develop
cd ..

# Set up systemd service
cat > /etc/systemd/system/tradebyte.service << EOF
[Unit]
Description=TradeByte Trading Platform
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/TradeByte
Environment=PATH=/home/ec2-user/TradeByte/venv/bin
ExecStart=/home/ec2-user/TradeByte/venv/bin/python src/apps/strategies/market_maker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl enable tradebyte
systemctl start tradebyte
```

#### 3. CloudFormation Template
```yaml
# tradebyte-cloudformation.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'TradeByte Trading Platform'

Parameters:
  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Name of an existing EC2 KeyPair

Resources:
  TradeByteInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316
      InstanceType: t3.medium
      KeyName: !Ref KeyName
      SecurityGroupIds:
        - !Ref TradeByteSecurityGroup
      SubnetId: !Ref SubnetId
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          # User data script content here
      Tags:
        - Key: Name
          Value: TradeByte-Instance

  TradeByteSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for TradeByte
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

Outputs:
  InstanceId:
    Description: Instance ID of the TradeByte instance
    Value: !Ref TradeByteInstance
```

### Google Cloud Platform

#### 1. Compute Engine Setup
```bash
# Create instance
gcloud compute instances create tradebyte-instance \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --metadata-from-file startup-script=startup-script.sh
```

#### 2. Startup Script
```bash
#!/bin/bash
# startup-script.sh

# Update system
apt-get update
apt-get install -y python3.10 python3.10-venv python3-pip

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env

# Clone and setup TradeByte
cd /home/ubuntu
git clone https://github.com/GoneInactive/TradeByte.git
cd TradeByte

python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd rust_client
maturin develop
cd ..

# Setup systemd service
cat > /etc/systemd/system/tradebyte.service << EOF
[Unit]
Description=TradeByte Trading Platform
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/TradeByte
Environment=PATH=/home/ubuntu/TradeByte/venv/bin
ExecStart=/home/ubuntu/TradeByte/venv/bin/python src/apps/strategies/market_maker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl enable tradebyte
systemctl start tradebyte
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tradebyte'
    static_configs:
      - targets: ['tradebyte:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Metrics Collection

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Define metrics
orders_placed = Counter('tradebyte_orders_placed_total', 'Total orders placed', ['side', 'pair'])
orders_filled = Counter('tradebyte_orders_filled_total', 'Total orders filled', ['side', 'pair'])
order_latency = Histogram('tradebyte_order_latency_seconds', 'Order placement latency')
websocket_connections = Gauge('tradebyte_websocket_connections', 'Active WebSocket connections')
memory_usage = Gauge('tradebyte_memory_usage_bytes', 'Memory usage in bytes')
cpu_usage = Gauge('tradebyte_cpu_usage_percent', 'CPU usage percentage')

class MetricsCollector:
    def __init__(self, port=9090):
        self.port = port
        start_http_server(port)
    
    def record_order_placed(self, side, pair):
        orders_placed.labels(side=side, pair=pair).inc()
    
    def record_order_filled(self, side, pair):
        orders_filled.labels(side=side, pair=pair).inc()
    
    def record_order_latency(self, duration):
        order_latency.observe(duration)
    
    def set_websocket_connections(self, count):
        websocket_connections.set(count)
    
    def update_system_metrics(self):
        import psutil
        memory_usage.set(psutil.virtual_memory().used)
        cpu_usage.set(psutil.cpu_percent())
```

### Logging Configuration

```python
# src/logging/config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_file="/var/log/tradebyte/tradebyte.log", level=logging.INFO):
    """Setup comprehensive logging"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=100*1024*1024,  # 100MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return root_logger
```

## Security Considerations

### API Key Management

```python
# src/security/key_management.py
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureKeyManager:
    def __init__(self, master_password):
        self.master_password = master_password.encode()
        self.fernet = self._create_fernet()
    
    def _create_fernet(self):
        """Create Fernet cipher from master password"""
        salt = b'tradebyte_salt'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
        return Fernet(key)
    
    def encrypt_api_key(self, api_key):
        """Encrypt API key"""
        return self.fernet.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key):
        """Decrypt API key"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()
    
    def store_encrypted_keys(self, api_key, api_secret):
        """Store encrypted API keys"""
        encrypted_key = self.encrypt_api_key(api_key)
        encrypted_secret = self.encrypt_api_key(api_secret)
        
        with open('config/encrypted_keys.txt', 'w') as f:
            f.write(f"{encrypted_key}\n{encrypted_secret}")
    
    def load_encrypted_keys(self):
        """Load and decrypt API keys"""
        with open('config/encrypted_keys.txt', 'r') as f:
            encrypted_key, encrypted_secret = f.read().strip().split('\n')
        
        return (
            self.decrypt_api_key(encrypted_key),
            self.decrypt_api_key(encrypted_secret)
        )
```

### Network Security

```bash
# Firewall configuration (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# SSL/TLS configuration
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Performance Optimization

### System Tuning

```bash
# /etc/sysctl.conf optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
```

### Application Optimization

```python
# src/optimization/performance.py
import asyncio
import psutil
from concurrent.futures import ThreadPoolExecutor

class PerformanceOptimizer:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.loop = asyncio.get_event_loop()
    
    async def optimize_websocket_connection(self, client):
        """Optimize WebSocket connection settings"""
        # Set TCP_NODELAY
        client._ws_connection.sock.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1
        )
        
        # Set buffer sizes
        client._ws_connection.sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, 65536
        )
        client._ws_connection.sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF, 65536
        )
    
    def optimize_memory_usage(self):
        """Optimize memory usage"""
        # Set garbage collection thresholds
        import gc
        gc.set_threshold(700, 10, 10)
        
        # Clear unnecessary caches
        import sys
        sys.modules.clear()
    
    async def run_in_thread_pool(self, func, *args):
        """Run CPU-intensive tasks in thread pool"""
        return await self.loop.run_in_executor(
            self.thread_pool, func, *args
        )
```

## Backup and Recovery

### Data Backup Strategy

```python
# src/backup/backup_manager.py
import shutil
import json
import gzip
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, backup_dir="/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self):
        """Create comprehensive backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"tradebyte_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir()
        
        # Backup configuration
        self._backup_config(backup_path)
        
        # Backup data
        self._backup_data(backup_path)
        
        # Backup logs
        self._backup_logs(backup_path)
        
        # Create compressed archive
        archive_path = f"{backup_path}.tar.gz"
        shutil.make_archive(str(backup_path), 'gztar', backup_path)
        
        # Clean up temporary directory
        shutil.rmtree(backup_path)
        
        return archive_path
    
    def _backup_config(self, backup_path):
        """Backup configuration files"""
        config_dir = backup_path / "config"
        config_dir.mkdir()
        
        if Path("config/config.yaml").exists():
            shutil.copy2("config/config.yaml", config_dir)
    
    def _backup_data(self, backup_path):
        """Backup market data"""
        data_dir = backup_path / "data"
        data_dir.mkdir()
        
        if Path("data").exists():
            shutil.copytree("data", data_dir, dirs_exist_ok=True)
    
    def _backup_logs(self, backup_path):
        """Backup log files"""
        logs_dir = backup_path / "logs"
        logs_dir.mkdir()
        
        if Path("logs").exists():
            shutil.copytree("logs", logs_dir, dirs_exist_ok=True)
    
    def restore_backup(self, backup_file):
        """Restore from backup"""
        import tarfile
        
        with tarfile.open(backup_file, 'r:gz') as tar:
            tar.extractall(path="/tmp/restore")
        
        restore_path = Path("/tmp/restore")
        
        # Restore configuration
        if (restore_path / "config").exists():
            shutil.copytree(restore_path / "config", "config", dirs_exist_ok=True)
        
        # Restore data
        if (restore_path / "data").exists():
            shutil.copytree(restore_path / "data", "data", dirs_exist_ok=True)
        
        # Clean up
        shutil.rmtree(restore_path)
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=30
LOG_FILE="/var/log/tradebyte/backup.log"

# Create backup
echo "$(date): Starting backup" >> $LOG_FILE
python3 -c "
from src.backup.backup_manager import BackupManager
manager = BackupManager('$BACKUP_DIR')
backup_file = manager.create_backup()
print(f'Backup created: {backup_file}')
" >> $LOG_FILE 2>&1

# Clean up old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date): Backup completed" >> $LOG_FILE
```

### Cron Job Setup

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/full_backup.sh
```

This comprehensive deployment guide covers all aspects of deploying TradeByte in various environments, from local development to production cloud deployments. Each section includes detailed instructions, configuration examples, and best practices for security, monitoring, and maintenance. 