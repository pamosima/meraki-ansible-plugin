FROM python:3.10-buster

# Install Ansible and sshpass
RUN python3 -m pip install ansible && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl sshpass


# Set working directory
WORKDIR /ansible

COPY src $USER/ansible/src
RUN cd src
RUN pip install -r requirements.txt