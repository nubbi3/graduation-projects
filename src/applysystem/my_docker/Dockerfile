FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y iputils-ping \
    && apt-get install -y net-tools \
    && apt-get install -y picocom \
    && apt-get install -y vim \
    && apt-get install -y tftp-hpa \
    && ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    # for SSH
    && apt-get install -y openssh-server \
    && apt-get install -y openssh-client \
    && apt-get install -y ssh

# 開機啟動SSH
ARG username
RUN mkdir -p ~/.ssh

COPY /ssh_keys/${username}/authorized_keys /root/.ssh
COPY config /root/.ssh/config
RUN /bin/bash -c 'chmod +x /root/.ssh/config'
RUN /bin/bash -c 'chmod +x /root/.ssh/authorized_keys'
RUN /bin/bash -c 'chmod -R go= /root/.ssh'
RUN /bin/bash -c 'chown -R root /root/.ssh'

COPY startup_run.sh /etc/startup_run.sh
RUN /bin/bash -c 'chmod +x /etc/startup_run.sh'

RUN echo "# startup run" >> /root/.bashrc
RUN echo "if [ -f /etc/startup_run.sh ]; then" >> /root/.bashrc
RUN echo "      /etc/startup_run.sh" >> /root/.bashrc
RUN echo "fi" >> /root/.bashrc

RUN sed -i "s/#Port 22/Port 10008/g" /etc/ssh/sshd_config
RUN sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config
RUN sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
RUN sed -i "s/UsePAM yes/UsePAM no/g" /etc/ssh/sshd_config

# 結束提示語句
COPY remind /etc/remind
RUN /bin/bash -c 'chmod +x /etc/remind'

# 記錄甪戶操作記錄配置
COPY .profile /root/.profile
RUN /bin/bash -c 'chmod +x /root/.profile'

COPY session.log /etc/session.log
RUN /bin/bash -c 'chmod +x /etc/session.log'

#Expose Port
EXPOSE 10008

CMD bash