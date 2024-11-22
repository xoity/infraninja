# InfraNinja Test Project

This project contains configuration and deployment scripts for managing virtual machines and deploying updates using Vagrant and Pyinfra. The deployment process integrates with an API to fetch server details dynamically using an access key provided by the user.

---

## Files Overview

### `Vagrantfile`
- **Purpose**: Defines the configuration for two virtual machines (VMs) managed by Vagrant.
  - **Ubuntu VM**: 1024 MB of memory and 2 CPU cores.
  - **Alpine VM**: 512 MB of memory and 1 CPU core.
- **Usage**: If you choose to test on VMs running on VBox, VMware, etc., then this sets up the VMs locally for testing deployment scripts.

### `test_deploy.py`
- **Purpose**: Executes deployment tasks using Pyinfra, a lightweight server management tool.
  - Includes a sample function to update packages on the configured VMs.
- **Details**: This script imports deployment modules from the `infraninja` folder to execute predefined tasks.

### `inventory.py`
- **Purpose**: Fetches server details from an API dynamically based on the user's access key.
  - Returns a list of servers with their IP addresses, SSH users, and SSH keys.
- **Details**: Uses environment variables (`ACCESS_KEY` and `INVENTORY_URL`) for secure access to an API.
  - Fetched server details are formatted for use in Pyinfra.

---

## Setting Up the Environment

### Prerequisites
1. **Install Vagrant**: Download and install Vagrant from the official [Vagrant website](https://www.vagrantup.com/downloads).
2. **Install VirtualBox or Another Provider**: Ensure you have a supported Vagrant provider, such as VirtualBox or VMware.
3. **Install Python & Pyinfra**: Install Python 3.x and Pyinfra:
   ```bash
   pip install pyinfra
   ```

### Initializing the Vagrant Environment
1. **Navigate to the Project Directory**: Open a terminal and navigate to the folder containing the `Vagrantfile`.
2. **Start the Virtual Machines**:
   ```bash
   vagrant up
   ```
   This command will provision the Ubuntu and Alpine VMs as specified in the `Vagrantfile`.
3. **Access the VMs**:
   - To SSH into the Ubuntu VM:
     ```bash
     vagrant ssh ubuntu
     ```
   - To SSH into the Alpine VM:
     ```bash
     vagrant ssh alpine
     ```

---

## Setting Up Environment Variables

### 1. Setting the `ACCESS_KEY`

The `inventory.py` script requires an access key to authenticate with an API and fetch server details dynamically. Follow these steps to set the `ACCESS_KEY` environment variable:

#### **How to Set the Access Key**:
- **Linux/macOS**:
  ```bash
  export ACCESS_KEY="your_access_key_here"
  ```
- **Windows (Command Prompt)**:
  ```cmd
  set ACCESS_KEY=your_access_key_here
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:ACCESS_KEY="your_access_key_here"
  ```

#### **Verify the Variable**:
- **Linux/macOS**:
  ```bash
  echo $ACCESS_KEY
  ```
- **Windows (Command Prompt)**:
  ```cmd
  echo %ACCESS_KEY%
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:ACCESS_KEY
  ```

---

### 2. Setting the `INVENTORY_URL`

If you need to use a custom API endpoint to fetch server details, you can set the `INVENTORY_URL` environment variable. This allows flexibility in pointing the inventory script to a different URL.

#### **How to Set the Inventory URL**:
- **Linux/macOS**:
  ```bash
  export INVENTORY_URL="https://custom-api-url.com/inventory/getServers/"
  ```
- **Windows (Command Prompt)**:
  ```cmd
  set INVENTORY_URL=https://custom-api-url.com/inventory/getServers/
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:INVENTORY_URL="https://custom-api-url.com/inventory/getServers/"
  ```

#### **Verify the Variable**:
- **Linux/macOS**:
  ```bash
  echo $INVENTORY_URL
  ```
- **Windows (Command Prompt)**:
  ```cmd
  echo %INVENTORY_URL%
  ```
- **Windows (PowerShell)**:
  ```powershell
  $env:INVENTORY_URL
  ```

---

### Using Both Variables Together

Ensure both `ACCESS_KEY` and `INVENTORY_URL` are set correctly before running the deployment scripts. If either variable is missing, the `inventory.py` script will fail to fetch server details from the API.

1. Example on Linux/macOS:
   ```bash
   export ACCESS_KEY="your_access_key_here"
   export INVENTORY_URL="https://custom-api-url.com/inventory/getServers/"
   ```

2. Example on Windows (Command Prompt):
   ```cmd
   set ACCESS_KEY=your_access_key_here
   set INVENTORY_URL=https://custom-api-url.com/inventory/getServers/
   ```

3. Example on Windows (PowerShell):
   ```powershell
   $env:ACCESS_KEY="your_access_key_here"
   $env:INVENTORY_URL="https://custom-api-url.com/inventory/getServers/"
   ```

---

## Running the Deployment

### Test Deployment with Pyinfra
To execute the test deployment defined in `test_deploy.py`:

1. **Ensure Environment Variables Are Set**: Make sure both `ACCESS_KEY` and `INVENTORY_URL` environment variables are properly configured.
2. **Run the Script**:
   ```bash
   python test_deploy.py
   ```
3. **Expected Behavior**:
   - The script fetches server details from an API.
   - It performs an update of packages on the retrieved servers.

---

## Adding New Functions in `test_deploy.py`

To run additional deployment tasks, you can import modules from `infraninja` or write new functions directly in `test_deploy.py`. Example:

1. **Create a New Task** in `infraninja/common/`:
   ```python
   from pyinfra.operations import apt

   def install_nginx():
       apt.packages(
           name="Install NGINX",
           packages=["nginx"],
           update=True
       )
   ```

2. **Import & Run the Task in `test_deploy.py`**:
   ```python
   from infraninja.common.nginx_setup import install_nginx

   @deploy("Install NGINX")
   def nginx_deploy():
       install_nginx()

   nginx_deploy()
   ```

3. **Execute the Script**:
   ```bash
   python test_deploy.py
   ```

---

## Troubleshooting

- **Access Key Not Set**:
  - Ensure the `ACCESS_KEY` environment variable is correctly configured.
  - Confirm the key has the necessary permissions in an API.

- **Inventory URL Missing**:
  - Verify the `INVENTORY_URL` variable points to the correct endpoint.
  - Test the endpoint using `curl` or similar tools.

- **VM Connection Issues**:
  - Check that the Vagrant VMs are running (`vagrant status`).
  - Verify the SSH settings (e.g., SSH key or username).
