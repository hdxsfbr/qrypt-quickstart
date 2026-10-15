# Qrypt Isolated Setup: the AI agent runs as user "agent" with NO access to
# QRYPT_API_KEY. Live verification happens OUTSIDE this container via verify.sh,
# which runs fixed snippets from the repo, never agent-writable code.
FROM node:24-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip ca-certificates curl git sudo \
 && rm -rf /var/lib/apt/lists/* \
 && userdel -r node 2>/dev/null || true \
 && useradd -m -u 1000 -s /bin/bash agent
# Mock Qrypt server + case runner are available for the agent to exercise.
# No .env, no token, no Docker socket, no host secrets.
WORKDIR /work
USER agent
ENV HOME=/home/agent
CMD ["bash"]
