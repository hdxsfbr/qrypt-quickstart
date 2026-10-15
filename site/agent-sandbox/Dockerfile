# Qrypt agent sandbox: the AI agent runs as user "agent" and cannot read .env.
# .env is written by the entrypoint, owned by user "qrypt" (mode 600). Only `qrypt-run` (a fixed sudo rule) runs your program as "qrypt".
FROM node:24-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv python3-pip sudo ca-certificates curl git \
 && rm -rf /var/lib/apt/lists/* \
 && userdel -r node && useradd -m -u 1000 -s /bin/bash agent && useradd -M -u 1500 -s /usr/sbin/nologin qrypt
COPY qrypt-run qrypt-run-inner entrypoint.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/qrypt-run /usr/local/bin/qrypt-run-inner /usr/local/bin/entrypoint.sh \
 && echo 'agent ALL=(qrypt) NOPASSWD: /usr/local/bin/qrypt-run-inner' > /etc/sudoers.d/qrypt && chmod 440 /etc/sudoers.d/qrypt
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
