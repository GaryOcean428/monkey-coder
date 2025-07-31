FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=18
ENV PYTHON_VERSION=3.11
ENV POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    jq \
    # Python dependencies
    python3-dev \
    python3-pip \
    python3-venv \
    # Node.js dependencies
    ca-certificates \
    gnupg \
    # Database clients
    postgresql-client \
    redis-tools \
    # Additional development tools
    sqlite3 \
    zip \
    unzip \
    software-properties-common \
    apt-transport-https \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and Yarn
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn@latest

# Install Python Poetry
RUN pip3 install poetry==${POETRY_VERSION}

# Install Python development tools
RUN pip3 install \
    black \
    isort \
    flake8 \
    mypy \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pre-commit \
    ipython \
    jupyterlab

# Set up workspace
WORKDIR /workspace

# Copy package files for dependency installation
COPY package.json yarn.lock* ./
COPY packages/cli/package.json ./packages/cli/
COPY packages/web/package.json ./packages/web/
COPY packages/sdk/package.json ./packages/sdk/
COPY docs/package.json ./docs/

# Install Node.js dependencies
RUN yarn install --frozen-lockfile

# Copy Python requirements
COPY requirements.txt requirements.in ./
COPY packages/core/pyproject.toml ./packages/core/
COPY packages/sdk/src/python/requirements.txt ./packages/sdk/src/python/

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Install development Python packages in editable mode
COPY packages/core ./packages/core
COPY packages/sdk/src/python ./packages/sdk/src/python
RUN cd packages/core && pip3 install -e . \
    && cd ../sdk/src/python && pip3 install -e .

# Set up Git configuration for the vscode user
USER vscode
RUN git config --global init.defaultBranch main \
    && git config --global core.editor "code --wait" \
    && git config --global pull.rebase false

# Install Oh My Zsh for better shell experience
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
    && echo 'export PATH="/workspace/node_modules/.bin:$PATH"' >> ~/.zshrc \
    && echo 'export PYTHONPATH="/workspace/packages/core:/workspace/packages/sdk/src/python:$PYTHONPATH"' >> ~/.zshrc

# Set up VS Code user settings
RUN mkdir -p /home/vscode/.config/Code/User
COPY .devcontainer/settings.json /home/vscode/.config/Code/User/

USER root
