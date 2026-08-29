FROM frrouting/frr:latest

RUN apk add --no-cache openssh-server sudo

RUN adduser -D -s /bin/sh netops \
    && echo 'netops ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/netops \
    && chmod 440 /etc/sudoers.d/netops

RUN ssh-keygen -A

RUN mkdir -p /home/netops/.ssh \
    && chmod 700 /home/netops/.ssh \
    && touch /home/netops/.ssh/authorized_keys \
    && chmod 600 /home/netops/.ssh/authorized_keys \
    && chown -R netops:netops /home/netops/.ssh

RUN printf '%s\n' \
    'PermitRootLogin no' \
    'PasswordAuthentication no' \
    'PubkeyAuthentication yes' \
    'UsePAM no' \
    'AllowUsers netops' \
    > /etc/ssh/sshd_config

CMD ["/bin/sh", "-c", "/usr/sbin/sshd && /usr/lib/frr/docker-start"]
