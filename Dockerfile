FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y pip curl less git
RUN pip install ansible-core==2.13.13
RUN pip install jmespath
RUN ansible-galaxy collection install community.general ansible.posix
RUN groupadd jtable_grp
RUN useradd -m -G jtable_grp jtable
WORKDIR /project/jtable
RUN echo 'set -o vi' >> /root/.bashrc
RUN echo 'alias ll="ls -lrt"' >> /root/.bashrc