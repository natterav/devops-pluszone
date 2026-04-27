pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                bat 'docker compose build'
            }
        }
        stage('Test') {
            steps {
                bat 'docker compose run --rm web pytest tests/ -v'
            }
        }
        stage('Deploy') {
            steps {
                bat 'docker compose up -d --force-recreate'
            }
        }
    }

    post {
        success {
            echo 'Deploy de PlusZone exitoso'
        }
        failure {
            echo 'Pipeline fallido - revisar logs'
        }
    }
}
