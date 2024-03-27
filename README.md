# Ansible Inventory Plugin for Meraki

The Meraki Inventory Plugin for Ansible simplifies the automation of device provisioning and VLAN configuration tasks for Cisco Catalyst switches. By seamlessly integrating with the Meraki Dashboard, this plugin streamlines network management processes, enhancing overall efficiency.

## Use Case Description

This plugin offers a comprehensive solution for automating device provisioning and VLAN configuration for Cisco Catalyst switches, thereby optimizing network management operations. Leveraging Ansible playbooks, it provides a seamless approach to modify VLAN configurations for Catalyst Switches monitored within the Meraki Dashboard.

![Get Dynamic Inventory from Meraki Dashboard for Ansible](img/MerakiAnsibleDemo.gif)

The project consists of two components:

### [Ansible Playbooks with the Ansible Inventory Plugin](#ansible-playbooks)

These playbooks facilitate the configuration of devices unsing the Ansible Inventory Plugin. The Ansible Inventory Plugin retrieves devices from the Meraki Dashboard.

### [GitLab CI/CD Integration](#gitlab-cicd-pipeline-explanation)

Integrate with GitLab CI/CD to automate the execution of Ansible playbooks for creating VLANs and changing L2 interface configurations.

## Installation

To install and configure the project:

1. Clone the repository:

   ```bash
   git clone https://github.com/pamosima/meraki-ansible-plugin meraki-ansible-plugin
   ```

2. Navigate to the repository directory:

   ```bash
   cd meraki-ansible-plugin
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

4. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Configure environment variables by creating the `.bash-script.sh` file:

   ```bash
   nano .bash-script.sh
   ```

   Adjust the environment variables as needed. Example:

   ```bash
   export MERAKI_API_KEY="<my-meraki-apy-key>"
   export MERAKI_ORG_ID="<my-meraki-org>"
   export ANSIBLE_HOST_KEY_CHECKING=false
   ```

7. Source the `.bash-script.sh` file to apply the environment variables:

   ```bash
   source .bash-script.sh
   ```

8. Create an ansible file for SSH Credentials

   In this, I have used ansible vault to create the credentials file for the SSH password & enable secret so that we can manage it safely.

   > **NOTE**: To create a new encrypted file using ansible vault you need to run the below command. It will ask for password so, please give a password that you can easily remember

   ```bash
   cd ansible
   ansible-vault create vars/cred.yml
   ```

   Add below content in it

   ```bash
   ansible_user: <my-username>
   ansible_ssh_pass: <my-password>
   absible_become_pass: <my-enable_secret>
   ```

9. Create a password file
   Create a new file called `.vault_password.txt` and add your ansible vault password in it so that we can use it later.

10. (Optional) Build the Docker image for the GitLab CI/CD runner:

    - Navigate to the Docker folder:

      ```bash
      cd gitlab-cicd/docker
      ```

    - Copy the downloaded files into the `docker` directory.

    - Build the Docker image using the following command:

      ```bash
      docker build -t ansible-runner .
      ```

Once the image is built successfully, you can use it as the base image for your GitLab CI/CD runner.

## Usage

### Ansible Playbooks

The Ansible Playbooks are located in the ansible subfolder.

#### Meraki Inventory Plugin

The meraki_devices inventory plugin allows you to create a dynamic inventory from the Meraki Dashboard.

```

cd ansible
ansible-inventory -i meraki_devices.yml --playbook-dir=. --list --yaml --vault-password-file=.vault_password.txt

```

#### Show Version Playbook

This Playbook is using the meraki_device Plugin and does a "show version".

```

ansible-playbook -i meraki_devices.yml show_version-playbook.yml --vault-password-file=.vault_password.txt

```

#### L2 Interface Configuration Playbook

This Playbook is using the meraki_device Plugin and configures the L2 interfaces of a Catalyst Switch based on the device variable YAML file.

```

ansible-playbook -i meraki_devices.yml l2_interface_config-playbook.yml --vault-password-file=.vault_password.txt

```

#### VLAN Configuration Playbook

This Playbook is using the meraki_device Plugin and configures VLAN(s) on Catalyst Switches based on vars/vlans.yaml.

```

ansible-playbook -i meraki_devices.yml vlan_config-playbook.yml --vault-password-file=.vault_password.txt

```

### GitLab CI/CD Pipeline Explanation

The GitLab CI/CD configuration defines two stages:

1. **deploy_l2_interface_config**: This stage is responsible for deploying L2 interface configurations using Ansible playbooks.

   - **Script**: It runs the Ansible playbook `l2_interface_config-playbook.yml`.
   - **Rules**:
     - It executes if the pipeline is triggered by a web (manual) action on the default branch and the pipeline variable `$PIPELINE_NAME` is `"l2"`.
     - It also executes if the pipeline is triggered by a push to the default branch, but only if there are changes in specific files related to L2 interface configurations.

2. **deploy_vlan_config**: This stage is responsible for deploying VLAN configurations using Ansible playbooks.
   - **Script**: It runs the Ansible playbook `vlan_config-playbook.yml`.
   - **Rules**:
     - It executes if the pipeline is triggered by a web (manual) action on the default branch and the pipeline variable `$PIPELINE_NAME` is `"vlan"`.
     - It also executes if the pipeline is triggered by a push to the default branch, but only if there are changes in specific files related to VLAN configurations.

#### Runner Configuration

The GitLab CI/CD runner for this pipeline is a Docker runner which includes meraki, pyats, ansible and paramiko for executing the Ansible playbooks.

## Known issues

Currently, there are no known issues. Please report any bugs or problems using the GitHub Issues section.

## Getting help

If you encounter any issues or need assistance, please create an issue in the GitHub repository for support.

## Getting involved

Contributions to this project are welcome! Please refer to the [CONTRIBUTING](./CONTRIBUTING.md) guidelines for instructions on how to contribute.

## Author(s)

This project was written and is maintained by the following individuals:

- Patrick Mosimann <pamosima@cisco.com>
