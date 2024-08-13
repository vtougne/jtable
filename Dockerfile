FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y pip
RUN echo 'set -o vi' >> /root/.bashrc
RUN echo 'alias ll="ls -lrt"' >> /root/.bashrc
RUN apt-get install -y curl less
RUN pip install ansible-core==2.13.13
RUN pip install jmespath
RUN ansible-galaxy collection install community.general ansible.posix
RUN echo localhost > /tmp/ansible_inventory.txt
RUN pip install tabulate
WORKDIR /project/jtable
RUN apt-get install -y git
# RUN ln -s /usr/bin/python3 /usr/bin/python