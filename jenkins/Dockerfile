FROM jenkins/jenkins:lts

USER root

# Set environment variables
ENV TERRAFORM_VERSION=1.6.6 \
    NODE_VERSION=24.0.2 \
    NVM_DIR=/usr/local/nvm

# Install base tools
RUN apt-get update && \
    apt-get install -y \
        curl \
        unzip \
        gnupg \
        ca-certificates \
        lsb-release \
        software-properties-common \
        openssl \
        apt-transport-https \
        git \
        sudo

# Install Terraform
RUN curl -fsSL https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -o terraform.zip && \
    unzip terraform.zip && \
    mv terraform /usr/local/bin/terraform && \
    rm terraform.zip

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Install Google Cloud SDK
RUN curl -sSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-sdk

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y docker-ce-cli

# Install Node.js (via NVM)
RUN mkdir -p $NVM_DIR && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install ${NODE_VERSION} && \
    nvm alias default ${NODE_VERSION} && \
    nvm use default && \
    ln -s $NVM_DIR/versions/node/v${NODE_VERSION}/bin/node /usr/local/bin/node && \
    ln -s $NVM_DIR/versions/node/v${NODE_VERSION}/bin/npm /usr/local/bin/npm && \
    ln -s $NVM_DIR/versions/node/v${NODE_VERSION}/bin/npx /usr/local/bin/npx

ENV PATH=$PATH:/usr/local/nvm/versions/node/v${NODE_VERSION}/bin

USER jenkins
