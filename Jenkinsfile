pipeline {
    agent any

    environment {
        PORT = '4000'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/natterav/devops-pluszone.git'
            }
        }

        stage('Setup Python') {
            steps {
                bat 'python --version'
                bat 'cd server && pip install -r requirements.txt'
            }
        }

        stage('Build') {
            steps {
                echo 'Building the application...'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
            }
        }

        stage('Deploy') {
            steps {
                bat 'taskkill /F /IM python.exe /T 2>nul || exit /b 0'
                bat 'cd server && start cmd /c "python app.py > app.log 2>&1"'
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
