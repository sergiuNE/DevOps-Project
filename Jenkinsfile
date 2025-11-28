pipeline {
    agent { label 'bletchley' }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build LTI Image') {
            steps {
                dir('ltitool') {
                    sh 'docker build -t sergiune/moodle-lti:${BUILD_NUMBER} .'
                    sh 'docker tag sergiune/moodle-lti:${BUILD_NUMBER} sergiune/moodle-lti:latest'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push sergiune/moodle-lti:${BUILD_NUMBER}'
                    sh 'docker push sergiune/moodle-lti:latest'
                    sh 'docker logout'
                }
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline succeeded!  Moodle stack deployed.'
        }
        failure {
            echo '❌ Pipeline failed!  Check logs.'
        }
    }
}