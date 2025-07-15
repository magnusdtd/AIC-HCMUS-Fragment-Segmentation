pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
    timestamps()
  }

  environment {
    // Docker image names for the three services
    BACKEND_IMAGE = 'magnusdtd/aic-hcmus-2025-backend'
    FRONTEND_IMAGE = 'magnusdtd/aic-hcmus-2025-frontend'
    CELERY_IMAGE = 'magnusdtd/aic-hcmus-2025-celery'
    
    // Full image names with latest tag
    BACKEND_FULL_IMAGE = "${BACKEND_IMAGE}:latest"
    FRONTEND_FULL_IMAGE = "${FRONTEND_IMAGE}:latest"
    CELERY_FULL_IMAGE = "${CELERY_IMAGE}:latest"
    
    DOCKER_REGISTRY_CREDENTIAL = 'dockerhub'
    
    // Credential IDs for sensitive data
    GOOGLE_CLIENT_ID_CREDENTIAL = 'google-client-id'
    GOOGLE_CLIENT_SECRET_CREDENTIAL = 'google-client-secret'
    SECRET_KEY_CREDENTIAL = 'secret-key'
    DB_PASSWORD_CREDENTIAL = 'db-password'
    MINIO_PASSWORD_CREDENTIAL = 'minio-password'
  }

  stages {

    stage('Run Tests') {
      steps {
        script {
          echo 'Running tests...'
          sh 'docker compose -f docker-compose.test.yml run --build --rm backend-test'
        }
      }
    }

    stage('Build Docker Images') {
      steps {
        script {
          echo 'Building all Docker images...'
          sh 'docker compose build'
          sh 'docker images'
        }
      }
    }

    stage('Push Docker Images') {
      steps {
        script {
          echo 'Pushing Docker images to the registry...'
          docker.withRegistry('', DOCKER_REGISTRY_CREDENTIAL) {
            // Push backend image
            echo "Pushing ${BACKEND_FULL_IMAGE}..."
            docker.image("${BACKEND_FULL_IMAGE}").push()
            
            // Push frontend image
            echo "Pushing ${FRONTEND_FULL_IMAGE}..."
            docker.image("${FRONTEND_FULL_IMAGE}").push()
            
            // Push celery image
            echo "Pushing ${CELERY_FULL_IMAGE}..."
            docker.image("${CELERY_FULL_IMAGE}").push()
          }
          echo 'All Docker images pushed successfully!'
        }
      }
    }

    stage('Deploy to Google Kubernetes Engine') {
      agent {
        kubernetes {
          yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: helm
                image: magnusdtd/jenkins-k8s:latest
                imagePullPolicy: Always
                command:
                - cat
                tty: true
          '''
        }
      }
      steps {
        script {
          container('helm') {

            // Load sensitive data from Jenkins credentials
            withCredentials([
              string(credentialsId: env.GOOGLE_CLIENT_ID_CREDENTIAL, variable: 'GOOGLE_CLIENT_ID'),
              string(credentialsId: env.GOOGLE_CLIENT_SECRET_CREDENTIAL, variable: 'GOOGLE_CLIENT_SECRET'),
              string(credentialsId: env.SECRET_KEY_CREDENTIAL, variable: 'SECRET_KEY'),
              string(credentialsId: env.DB_PASSWORD_CREDENTIAL, variable: 'DB_PASSWORD'),
              string(credentialsId: env.MINIO_PASSWORD_CREDENTIAL, variable: 'MINIO_PASSWORD')
            ]) {
              
              // Store credentials in environment variables for later stages
              env.GOOGLE_CLIENT_ID = GOOGLE_CLIENT_ID
              env.GOOGLE_CLIENT_SECRET = GOOGLE_CLIENT_SECRET
              env.SECRET_KEY = SECRET_KEY
              env.DB_PASSWORD = DB_PASSWORD
              env.MINIO_PASSWORD = MINIO_PASSWORD

              sh '''
                echo "Starting Helm deployment..."
                
                # Check if namespace exists, create if it doesn't
                kubectl get namespace aic-hcmus-app || kubectl create namespace aic-hcmus-app
                kubectl get namespace aic-hcmus-monitor || kubectl create namespace aic-hcmus-monitor
                
                # Check if release exists to determine install vs upgrade
                if helm list -n aic-hcmus-app | grep -q "aic-hcmus-prod"; then
                  echo "Release aic-hcmus-prod exists, performing upgrade..."
                  helm upgrade aic-hcmus-prod ./k8s/helm \
                    --set secrets.googleClientId="${GOOGLE_CLIENT_ID}" \
                    --set secrets.googleClientSecret="${GOOGLE_CLIENT_SECRET}" \
                    --set secrets.secretKey="${SECRET_KEY}" \
                    --set secrets.dbPassword="${DB_PASSWORD}" \
                    --set secrets.minioPassword="${MINIO_PASSWORD}" \
                    -n aic-hcmus-app --wait --timeout=10m
                else
                  echo "Release aic-hcmus-prod does not exist, performing install..."
                  helm install aic-hcmus-prod ./k8s/helm \
                    --set secrets.googleClientId="${GOOGLE_CLIENT_ID}" \
                    --set secrets.googleClientSecret="${GOOGLE_CLIENT_SECRET}" \
                    --set secrets.secretKey="${SECRET_KEY}" \
                    --set secrets.dbPassword="${DB_PASSWORD}" \
                    --set secrets.minioPassword="${MINIO_PASSWORD}" \
                    -n aic-hcmus-app --wait --timeout=10m
                fi
                
                echo "Helm deployment completed successfully!"
              '''
            }
          }
        }
      }
    }

  }

  post {
    success {
      script {
        echo 'Build successful.'
      }
    }
    failure {
      script {
        echo 'Build failed!'
      }
    }
    cleanup {
      script {
        echo 'Cleaning up...'
        sh 'docker image prune -f'
      }
    }
  }
}