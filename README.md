# vav-monitoring-system

## Overview
A FastAPI backend with MySQL database and web frontend for monitoring and controlling Variable Air Volume (VAV) units. The system automatically updates temperature setpoints every 10 seconds and provides a web interface for real-time monitoring and manual adjustments.

## Features
- Automatic temperature setpoint updates every 10 seconds
- Real-time monitoring of all VAV parameters
- Manual temperature setpoint adjustment
- Historical data tracking with timestamps
- Responsive web interface

## Prerequisites
- Python 3.7+
- MySQL Server
- Modern web browser

## Installation

### 1. Database Setup
```bash
mysql -u root -p
CREATE DATABASE vav_monitoring_system;
USE vav_monitoring_system;

CREATE TABLE IF NOT EXISTS devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(50) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    device_address INT NOT NULL,
    test_csv VARCHAR(10),
    UNIQUE KEY (device_name, device_type, device_address)
);

CREATE TABLE IF NOT EXISTS vav_data (
    data_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    vav_unit VARCHAR(10) NOT NULL,
    point_type ENUM('analogInput', 'analogValue') NOT NULL,
    point_address INT NOT NULL,
    parameter_name VARCHAR(50) NOT NULL,
    parameter_value DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    UNIQUE KEY (vav_unit, point_type, point_address, parameter_name)
);

-- Insert sample data (see full schema in setup.sql)
```

### 2. Backend Setup
```bash
# Clone repository
git clone https://github.com/your-repo/vav-monitoring-system.git
cd vav-monitoring-system

# Install dependencies
pip install -r requirements.txt

# Configure database connection
cp config.example.py config.py
# Edit config.py with your database credentials

# Run the backend
uvicorn main:app --reload
```

### 3. Frontend Setup
No installation needed - just open `index.html` in your browser.
