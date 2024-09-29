FROM ubuntu:22.04
RUN apt-get update && apt-get install -y sudo
RUN groupadd jtable
# RUN useradd -m -G jtable_grp jtable
RUN useradd -m -s /bin/bash jtable
RUN usermod -aG sudo jtable
RUN echo "jtable ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER jtable
ENV PATH="${PATH}:/home/jtable/.local/bin"
RUN sudo apt-get update
RUN sudo apt-get install -y pip curl less git
RUN pip install ansible-core==2.13.13
RUN pip install jmespath
RUN ansible-galaxy collection install community.general ansible.posix
WORKDIR /project/jtable
RUN echo 'set -o vi' >> /home/jtable/.bashrc
RUN echo 'alias ll="ls -lrt"' >> /home/jtable/.bashrc