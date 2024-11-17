FROM ubuntu:22.04
RUN apt-get update && apt-get install -y sudo
RUN groupadd jtable
RUN useradd -m -g jtable jtable
RUN usermod -aG sudo jtable
RUN echo "jtable ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER jtable
RUN sudo apt-get update
RUN sudo apt-get install -y pip curl less git

WORKDIR /project/jtable
RUN echo 'set -o vi' >> /home/jtable/.bashrc
RUN echo 'alias ll="ls -lrt"' >> /home/jtable/.bashrc
ENV PATH="${PATH}:/home/jtable/.local/bin"

RUN pip install ansible-core
RUN pip install jmespath
RUN ansible-galaxy collection install community.general ansible.posix

# CMD ["/bin/echo", “hello”]
# ENTRYPOINT ["/bin/sh"]
# ENTRYPOINT ["/bin/sh"]



# RUN pip install -r /project/jtable/requirements.txt