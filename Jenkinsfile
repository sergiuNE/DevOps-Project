pipeline {
    agent { label 'bletchley' }

    triggers {
        pollSCM('H/20 * * * *')  // Elke 20 minuten checken
    }

    options {
        skipStagesAfterUnstable()
    }
    
    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-creds')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Prepare Secrets') {
            steps {
                script {
                    sh 'mkdir -p secrets'
                    withCredentials([
                        string(credentialsId: 'db-root-password', variable: 'DB_ROOT_PW'),
                        string(credentialsId: 'db-password', variable: 'DB_PW'),
                        string(credentialsId: 'session-secret', variable: 'SESSION_SEC'),
                        string(credentialsId: 'oauth-secret', variable: 'OAUTH_SEC')
                    ]) {
                        sh '''
                            echo "$DB_ROOT_PW" > secrets/db_root_password.txt
                            echo "$DB_PW" > secrets/db_password.txt
                            echo "$SESSION_SEC" > secrets/session_secret.txt
                            echo "$OAUTH_SEC" > secrets/oauth_secret.txt
                            chmod 600 secrets/*.txt
                        '''
                    }
                }
            }
        }
        
        stage('Build LTI Image') {
            steps {
                dir('ltitool') {
                    sh 'docker build -t sergiune/moodle-lti:3 .'
                    sh 'docker tag sergiune/moodle-lti:3 sergiune/moodle-lti:latest'
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push sergiune/moodle-lti:3'
                    sh 'docker push sergiune/moodle-lti:latest'
                    sh 'docker logout'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    docker compose pull ltitool
                    docker compose up -d --force-recreate ltitool
                '''
            }
        }
    }
    
    post {
        failure {
            echo '❌ Pipeline failed!  Check logs.'
        }
        success {
            echo '✅ Pipeline succeeded!  LTI tool deployed.'
        }
    }
}