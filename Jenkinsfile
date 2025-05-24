pipeline {
    agent any
    environment {
        GOOGLE_CREDENTIALS = credentials('gcp-service-account')
        CLUSTER_NAME = 'my-gke-cluster'
        CLUSTER_ZONE = 'us-central1'
        PROJECT_ID = 'aic-hcmus'
        DB_USER = credentials('db-user')
        DB_PASSWORD = credentials('db-password')
        MINIO_USER = credentials('minio-user')
        MINIO_PASSWORD = credentials('minio-password')
        SECRET_KEY = credentials('secret-key')
    }
    stages {
        stage('Checkout') {
            steps {
              git branch: 'deploy', url: 'https://github.com/magnusdtd/AIC-HCMUS-Fragment-Segmentation.git'
            }
        }

        stage('Install OpenSSL and Create TLS Files') {
            steps {
                sh '''
                mkdir -p nginx-ssl
                openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                  -keyout nginx-ssl/tls.key -out nginx-ssl/tls.crt \
                  -subj "/CN=aic-hcmus-noobers.duckdns.org"
                '''
            }
        }

        stage('Replace Placeholders in YAML Files') {
            steps {
                sh '''
                sed -i "s/{{MINIO_USER}}/$MINIO_USER/g" k8s/app.yaml
                sed -i "s/{{MINIO_PASSWORD}}/$MINIO_PASSWORD/g" k8s/app.yaml
                sed -i "s/{{DB_USER}}/$DB_USER/g" k8s/app.yaml
                sed -i "s/{{DB_PASSWORD}}/$DB_PASSWORD/g" k8s/app.yaml
                sed -i "s/{{SECRET_KEY}}/$SECRET_KEY/g" k8s/app.yaml
                sed -i "s/{{DB_USER}}/$DB_USER/g" k8s/postgres.yaml
                sed -i "s/{{DB_PASSWORD}}/$DB_PASSWORD/g" k8s/postgres.yaml
                sed -i "s/{{MINIO_USER}}/$MINIO_USER/g" k8s/minio.yaml
                sed -i "s/{{MINIO_PASSWORD}}/$MINIO_PASSWORD/g" k8s/minio.yaml
                sed -i "s/{{DB_USER}}/$DB_USER/g" k8s/postgres-exporter.yaml
                sed -i "s/{{DB_PASSWORD}}/$DB_PASSWORD/g" k8s/postgres-exporter.yaml
                '''
            }
        }

        stage('Authenticate to GCP') {
            steps {
                sh '''
                echo $GOOGLE_CREDENTIALS > gcp-creds.json
                gcloud auth activate-service-account --key-file=gcp-creds.json
                gcloud config set project $PROJECT_ID
                '''
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                sh '''
                docker build -t gcr.io/$PROJECT_ID/app:latest .
                docker push gcr.io/$PROJECT_ID/app:latest
                docker build -t gcr.io/$PROJECT_ID/celery:latest -f backend/app/predict/Dockerfile .
                docker push gcr.io/$PROJECT_ID/celery:latest
                '''
            }
        }

        stage('Terraform Init') {
            steps {
                sh '''
                cd terraform
                terraform init
                '''
            }
        }

        stage('Terraform Apply') {
            steps {
                input "Apply infrastructure changes?"
                sh '''
                cd terraform
                terraform apply -auto-approve
                '''
            }
        }

        stage('Configure kubectl') {
            steps {
                sh '''
                gcloud container clusters get-credentials $CLUSTER_NAME --region $CLUSTER_ZONE
                kubectl version --short
                '''
            }
        }

        stage('Create TLS Secret') {
            steps {
                sh '''
                kubectl apply -f k8s/namespace.yaml
                kubectl delete secret nginx-ssl --namespace=aic-hcmus-app --ignore-not-found
                kubectl create secret tls nginx-ssl \
                  --cert=nginx-ssl/tls.crt \
                  --key=nginx-ssl/tls.key \
                  --namespace=aic-hcmus-app
                '''
            }
        }

        stage('Create Grafana ConfigMaps') {
            steps {
                sh '''
                kubectl apply -f k8s/namespace.yaml

                kubectl delete configmap grafana-dashboards -n aic-hcmus-monitor --ignore-not-found
                kubectl create configmap grafana-dashboards \
                  --from-file=grafana/dashboards \
                  -n aic-hcmus-monitor

                kubectl delete configmap grafana-provisioning-alerting -n aic-hcmus-monitor --ignore-not-found
                kubectl create configmap grafana-provisioning-alerting \
                  --from-file=grafana/provisioning/alerting \
                  -n aic-hcmus-monitor

                kubectl delete configmap grafana-provisioning-datasources -n aic-hcmus-monitor --ignore-not-found
                kubectl create configmap grafana-provisioning-datasources \
                  --from-file=grafana/provisioning/datasources \
                  -n aic-hcmus-monitor

                kubectl delete configmap grafana-provisioning-dashboards -n aic-hcmus-monitor --ignore-not-found
                kubectl create configmap grafana-provisioning-dashboards \
                  --from-file=grafana/provisioning/dashboards \
                  -n aic-hcmus-monitor
                '''
            }
        }

        stage('Deploy to GKE') {
            steps {
                sh '''
                kubectl apply -f k8s/minio.yaml
                kubectl apply -f k8s/postgres.yaml
                kubectl apply -f k8s/redis.yaml
                sleep 15
                kubectl apply -f k8s/app.yaml
                kubectl apply -f k8s/celery.yaml
                kubectl apply -f k8s/nginx.yaml

                kubectl apply -f k8s/celery-exporter.yaml
                kubectl apply -f k8s/node-exporter.yaml
                kubectl apply -f k8s/postgres-exporter.yaml
                kubectl apply -f k8s/redis-exporter.yaml
                kubectl apply -f k8s/prometheus.yaml
                kubectl apply -f k8s/grafana.yaml
                '''
            }
        }
    }
}
