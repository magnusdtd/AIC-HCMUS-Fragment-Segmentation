# Variables
SHELL := /bin/bash
SSH_KEY_DIR := secrets
SSH_KEY_PATH := $(SSH_KEY_DIR)/jenkins_key
TERRAFORM_DIR := terraform
ANSIBLE_DIR := ansible
REQUIRED_DIRS := $(SSH_KEY_DIR) $(TERRAFORM_DIR) $(ANSIBLE_DIR)
INVENTORY_FILE := $(ANSIBLE_DIR)/inventory/inventory.ini

# Colors for output
GREEN := \033[0;36m
RED := \033[0;35m
YELLOW := \033[0;33m
NC := \033[0m

# ---------------------------------------------------------------------------------#
# Utilities                                                                        #
# ---------------------------------------------------------------------------------#
# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@grep -E '^\.[PHONY]+: [a-zA-Z0-9_-]+.*$$' $(MAKEFILE_LIST) | awk '{print "  make " $$2}'

# Check and create required directories
.PHONY: check-dirs
check-dirs:
	@if [ -z "$(REQUIRED_DIRS)" ]; then \
		echo -e "$(RED)Error: REQUIRED_DIRS is not defined$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)Checking required directories...$(NC)"
	@for dir in $(REQUIRED_DIRS); do \
		if [ ! -d $$dir ]; then \
			echo -e "$(YELLOW)Creating directory: $$dir$(NC)"; \
			mkdir -p $$dir || { echo -e "$(RED)Failed to create directory: $$dir$(NC)"; exit 1; }; \
		else \
			echo -e "$(GREEN)Directory exists: $$dir$(NC)"; \
		fi; \
	done
	@echo -e "$(GREEN)Directory check complete$(NC)"
# ---------------------------------------------------------------------------------#

# ---------------------------------------------------------------------------------#
# Create SSH keys in order to make a Jnekins server in GCP
# ---------------------------------------------------------------------------------#
# Check SSH key permissions
.PHONY: check-ssh-perms
check-ssh-perms:
	@if [ -f $(SSH_KEY_PATH) ]; then \
		chmod 600 $(SSH_KEY_PATH) || { echo -e "$(RED)Failed to set permissions for $(SSH_KEY_PATH)$(NC)"; exit 1; }; \
		chmod 644 $(SSH_KEY_PATH).pub || { echo -e "$(RED)Failed to set permissions for $(SSH_KEY_PATH).pub$(NC)"; exit 1; }; \
		echo -e "$(GREEN)SSH key permissions set correctly$(NC)"; \
	else \
		echo -e "$(RED)SSH key not found at $(SSH_KEY_PATH)$(NC)"; \
		exit 1; \
	fi

# Generate SSH keys
.PHONY: genkey
genkey: check-dirs
	@echo -e "$(GREEN)Generating SSH key pair...$(NC)"
	@if [ ! -f $(SSH_KEY_PATH) ]; then \
		ssh-keygen -t rsa -b 2048 -f $(SSH_KEY_PATH) -C "magnusdtd" -N "" || { echo -e "$(RED)Failed to generate SSH key pair$(NC)"; exit 1; }; \
		echo -e "$(GREEN)SSH key pair generated successfully$(NC)"; \
	else \
		echo -e "$(YELLOW)SSH key already exists at $(SSH_KEY_PATH)$(NC)"; \
	fi
	@$(MAKE) check-ssh-perms
# ---------------------------------------------------------------------------------#


# ---------------------------------------------------------------------------------#
# Use Terraform to setup cluster									               #
# ---------------------------------------------------------------------------------#
.PHONY: tf-init
tf-init:
	@echo -e "$(GREEN)Initializing Terraform...$(NC)"
	cd $(TERRAFORM_DIR) && terraform init

.PHONY: tf-plan
tf-plan:
	@echo -e "$(GREEN)Planning Terraform changes...$(NC)"
	cd $(TERRAFORM_DIR) && terraform plan

.PHONY: tf-apply
tf-apply:
	@echo -e "$(GREEN)Applying Terraform changes...$(NC)"
	cd $(TERRAFORM_DIR) && terraform apply -auto-approve

.PHONY: tf-destroy
tf-destroy:
	@echo -e "$(GREEN)Destroying Terraform resources...$(NC)"
	cd $(TERRAFORM_DIR) && terraform destroy -auto-approve

.PHONY: tf-fmt
tf-fmt:
	@echo -e "$(GREEN)Formatting Terraform files...$(NC)"
	cd $(TERRAFORM_DIR) && terraform fmt -recursive

.PHONY: tf-validate
tf-validate:
	@echo -e "$(GREEN)Validating Terraform configuration...$(NC)"
	cd $(TERRAFORM_DIR) && terraform validate

.PHONY: tf-output
tf-output:
	@echo -e "${GREEN}Show Terraform outputs$(NC)"
	cd $(TERRAFORM_DIR) && terraform output

.PHONY: tf-clean
tf-clean:
	@echo -e "$(GREEN)Cleaning up Terraform files...$(NC)"
	@find $(TERRAFORM_DIR) -type f \( -name ".terraform*" -o -name "terraform.*" \) -exec rm -f {} +
	@find $(TERRAFORM_DIR) -type d -name ".terraform" -exec rm -rf {} +

# ---------------------------------------------------------------------------------#

# ---------------------------------------------------------------------------------#
# Use Ansible playbooks to deploy Jenkins server																	 #
# ---------------------------------------------------------------------------------#
.PHONY: ansible-deploy
ansible-deploy:
	@echo -e "$(GREEN)Running Ansible playbooks to create compute instance and deploy Jenkins...$(NC)"
	ansible-playbook $(ANSIBLE_DIR)/create_compute_instance.yaml
	ansible-playbook -i $(INVENTORY_FILE) $(ANSIBLE_DIR)/deploy_jenkins.yaml
	@echo -e "$(GREEN)Ansible playbooks executed successfully$(NC)"

.PHONY: ansible-destroy
ansible-destroy:
	@echo -e "$(GREEN)Destroying Ansible-created resources...$(NC)"
	ansible-playbook $(ANSIBLE_DIR)/destroy_compute_instance.yaml
	@echo -e "$(GREEN)Ansible resources destroyed successfully$(NC)"
# ---------------------------------------------------------------------------------#

.PHONY: destroy-all
destroy-all:
	@echo -e "$(GREEN)Destroying all infrastructure resources...$(NC)"
	@echo -e "$(YELLOW)Step 1: Destroying Ansible resources (compute instance)...$(NC)"
	@$(MAKE) ansible-destroy || true
	@echo -e "$(YELLOW)Step 2: Destroying Terraform resources (GKE cluster, network)...$(NC)"
	@$(MAKE) tf-destroy
	@$(MAKE) tf-clean
	@echo -e "$(GREEN)All infrastructure resources destroyed successfully$(NC)"

.PHONY: clean-ssh-keys
clean-ssh-keys:
	@echo -e "$(GREEN)Cleaning up SSH keys...$(NC)"
	@rm -f $(SSH_KEY_PATH) $(SSH_KEY_PATH).pub || true
	@echo -e "$(GREEN)SSH keys cleaned up successfully$(NC)"

.PHONY: full-cleanup
full-cleanup:
	@echo -e "$(GREEN)Performing full cleanup of all resources and files...$(NC)"
	@$(MAKE) destroy-all
	@$(MAKE) clean-ssh-keys
	@echo -e "$(GREEN)Full cleanup completed successfully$(NC)"
