# Infrastructure as Code (IaC) for GKE: Jenkins, Terraform, Ansible

This directory contains scripts and configuration to provision, deploy, and manage a Google Kubernetes Engine (GKE) cluster using Terraform, Ansible, and Jenkins for CI/CD automation.

---

## 📁 Folder Structure

```
./iac/
├── ansible/                           # Ansible playbooks for provisioning and managing Jenkins server
│   ├── create_compute_instance.yaml   # Create a GCE VM for Jenkins
│   ├── deploy_jenkins.yaml            # Install Docker & Jenkins on the VM
│   ├── destroy_compute_instance.yaml  # Destroy the Jenkins VM and clean up
│   └── inventory/                     # Ansible inventory files
│       └── inventory.ini
├── terraform/                         # Terraform scripts for GCP infrastructure
│   ├── main.tf                        # Main infrastructure definitions (VPC, GKE, etc.)
│   ├── variables.tf                   # Input variables for Terraform
│   ├── outputs.tf                     # Output values (e.g., cluster name, connect command)
│   └── .terraform/                    # Terraform state and provider plugins (auto-generated)
├── secrets/                           # Sensitive credentials (not versioned)
│   ├── <service-account>.json         # GCP service account key
│   ├── jenkins_key                    # SSH private key for Jenkins VM
│   └── jenkins_key.pub                # SSH public key
├── Makefile                           # Automation commands for common tasks
└── Readme.md                          # This documentation
```

---

## Table of Contents
- [I. Introduction](#i-introduction)
- [II. GKE Cluster Setup](#ii-setup-gke-cluster)
- [III. CI/CD with Jenkins & Ansible](#iii-continuous-integrationcontinuous-deployment-cicd-with-jenkins-and-ansible)
- [IV. Resources](#iv-resources)

---

## I. Introduction
This guide helps you automate the deployment of a GKE-based application using Infrastructure as Code (IaC) principles. It leverages:
- **Terraform** for provisioning GCP resources (VPC, GKE, etc.)
- **Ansible** for VM and Jenkins setup
- **Jenkins** for CI/CD pipelines

---

## II. Setup GKE Cluster

### 1. Install Terraform & Ansible
Install the required tools:
```sh
sudo apt update && sudo apt install software-properties-common gnupg2 curl
curl https://apt.releases.hashicorp.com/gpg | gpg --dearmor > hashicorp.gpg
sudo install -o root -g root -m 644 hashicorp.gpg /etc/apt/trusted.gpg.d/
sudo apt-add-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt install terraform ansible
```
Check versions:
```sh
terraform --version
ansible --version
```

### 2. Generate SSH Keys for Jenkins Server
To create an SSH key pair for the Jenkins server, go to the `iac` folder and run:
```sh
make genkey
```
This will generate `jenkins_key` (private) and `jenkins_key.pub` (public) in the `secrets/` directory. The keys are used for secure SSH access to the Jenkins VM provisioned by Ansible.

### 3. Prepare Credentials
- Create a folder named `secrets` at `iac/secrets`.
- Place your GCP service account JSON key in this folder.
- Update the credential file name in `iac/terraform/variables.tf`, `iac/ansible/create_compute_instance.yaml`, and `destroy_compute_instance.yaml` as needed.

### 4. Generate a Self-Signed SSL Certificate
At the project root:
```sh
mkdir -p nginx-ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx-ssl/tls.key \
  -out nginx-ssl/tls.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"
```

### 5. Enable Kubernetes Engine API
Enable the GKE API in your GCP project (via the GCP Console or CLI).

### 6. Provision GCP Infrastructure with Terraform
```sh
cd iac
make tf-init      # Initialize Terraform
make tf-apply     # Apply Terraform plan (provisions VPC, GKE, etc.)
```

### 7. Deploy to GKE Cluster
Create namespaces:
```sh
kubectl create ns aic-hcmus-app
kubectl create ns aic-hcmus-monitor
```
Create SSL secret:
```sh
kubectl create secret tls nginx-ssl --cert="path-to-the-cert-file" --key="path-to-the-key-file" -n aic-hcmus-app
```
Deploy with Helm:
```sh
helm install aic-hcmus-fragment-segmentation ./k8s/helm \
  --set secrets.googleClientId="your-client-id" \
  --set secrets.googleClientSecret="your-client-secret" \
  --set secrets.secretKey="your-secret-key" \
  --set secrets.dbPassword="your-db-password" \
  --set secrets.minioPassword="your-minio-password"
```

---

## III. Continuous Integration/Continuous Deployment (CI/CD) with Jenkins & Ansible

### 1. Provision Jenkins Server with Ansible
```sh
make ansible-deploy
```

### 2. Jenkins Installation & Access
- SSH into the Jenkins VM (IP is in `ansible/inventory/inventory.ini`):
  ```sh
  ssh -i secrets/jenkins_key <your-username>@<GCE_EXTERNAL_IP>
  ```
- Retrieve Jenkins admin password:
  ```sh
  sudo docker exec jenkins-k8s cat /var/jenkins_home/secrets/initialAdminPassword
  ```
- Access Jenkins UI at: `http://<GCE_EXTERNAL_IP>:8080`

### 3. Install Jenkins Plugins
Install these plugins:
- Docker
- Docker Pipeline
- Kubernetes
- Google Kubernetes Engine

Restart Jenkins after plugin installation:
```sh
sudo docker restart jenkins-k8s
```

### 4. Configure Jenkins
- **GitHub Webhook:** Add a webhook in your GitHub repo pointing to `http://<EXTERNAL_IP>:8080/github-webhook/` (select Push and Pull Request events).
- **Source Code:** In Jenkins, create a Multibranch Pipeline and connect it to your GitHub repo (add credentials as needed).
- **Docker Hub Credentials:** Add your Docker Hub username and access token in Jenkins credentials (ID: `dockerhub`).
- **Kubernetes Credentials:**
  1. Create a GCP Service Account with Kubernetes Engine Admin role and download its JSON key.
  2. In Jenkins, add a new Kubernetes cloud and provide cluster details and credentials.
  3. To get the cluster certificate:
     ```sh
     openssl s_client -connect <CLUSTER_ENDPOINT>:443 -showcerts </dev/null 2>/dev/null | openssl x509 -outform PEM > cluster-cert.pem
     ```

### 5. Trigger Jenkins Pipeline
Push a commit to your repository to trigger the Jenkins pipeline.

---

## IV. Reference Resources
- [Ansible Documentation](https://docs.ansible.com/ansible/latest/index.html)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started)
- [ChatOpsLLM: Effortless MLOps for Powerful Language Models](https://github.com/bmd1905/ChatOpsLLM)
- [Face Detection ML System](https://github.com/DucLong06/face-detection-ml-system)
- [End To End Agentic RAG Workflow for Answering Vietnamese Legal Traffic questions](https://github.com/meowwkhoa/End-To-End-Agentic-RAG-Workflow-for-Answering-Vietnamese-Legal-Traffic-questions)