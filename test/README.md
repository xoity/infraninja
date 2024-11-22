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

## Running the Deployment

### Test Deployment with Pyinfra
To execute the test deployment defined in `test_deploy.py`:

1. **Ensure Environment Variables Are Set**: Make sure both `ACCESS_KEY` and `INVENTORY_URL` environment variables are properly configured.
2. **Run the Script**:
   ```bash
   pyinfra inventory.py test_deploy.py
   ```
3. **Expected Behavior**:
   
   - Takes in your input for the API key and the URL
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
       install_nginx() # you may add "_sudo = True" if you need this to run with root

   nginx_deploy()
   ```

3. **Execute the Script**:
   ```bash
   pyinfra inventory.py test_deploy.py
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
