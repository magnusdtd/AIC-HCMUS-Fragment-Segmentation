pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
    timestamps()
  }

  environment {
    DOCKER_IMAGE = 'magnusdtd/jenkins-practice-app'
    DOCKER_FULL_IMAGE = "${DOCKER_IMAGE}:latest"
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
          // sh 'make install && make test'
          // I will add testcases later
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          sh 'docker compose build'
          sh 'docker images'
        }
      }
    }

    stage('Push Docker Image') {
      steps {
        script {
            echo 'Pushing Docker image to the registry...'
            docker.withRegistry('', DOCKER_REGISTRY_CREDENTIAL) {
              docker.image("${DOCKER_FULL_IMAGE}").push()
            }
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
            withCredentials([
              string(credentialsId: env.GOOGLE_CLIENT_ID, variable: 'GOOGLE_CLIENT_ID'),
              string(credentialsId: env.GOOGLE_CLIENT_SECRET, variable: 'GOOGLE_CLIENT_SECRET'),
              string(credentialsId: env.SECRET_KEY, variable: 'SECRET_KEY'),
              string(credentialsId: env.DB_PASSWORD, variable: 'DB_PASSWORD'),
              string(credentialsId: env.MINIO_PASSWORD, variable: 'MINIO_PASSWORD')
            ]) {
              sh '''
                echo "Starting Helm deployment..."
                echo "Chart path: ./k8s/helm"
                echo "Release name: aic-hcmus-prod"
                echo "Namespace: aic-hcmus-app"
                
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