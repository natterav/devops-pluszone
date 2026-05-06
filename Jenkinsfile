pipeline {
    agent any

    environment {
        // Define environment variables if needed
        NODE_ENV = 'production'
        PORT = '4000'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from GitHub
                git branch: 'main', url: 'https://github.com/natterav/devops-pluszone.git'
            }
        }

        stage('Setup Python') {
            steps {
                // Install Python if not available, or use a specific version
                bat 'python --version'
                // Install dependencies
                bat 'cd server && pip install -r requirements.txt'
            }
        }

        stage('Build') {
            steps {
                // Any build steps if needed, e.g., compile assets
                echo 'Building the application...'
                // For example, if client has build process, but since it's vanilla JS, maybe not needed
            }
        }

        stage('Test') {
            steps {
                // Run tests if you have them
                echo 'Running tests...'
                // sh 'cd server && python3 -m pytest'  // If you add tests later
            }
        }

        stage('Deploy') {
            steps {
                // Deploy the application
                bat 'echo Deploying the application...'
                // Stop any existing process
                bat 'taskkill /F /IM python.exe /FI "WINDOWTITLE eq python app.py" || echo No process found'
                // Start the new application
                bat 'cd server && start cmd /c "python app.py > app.log 2>&1"'
                // Or use a process manager like systemd, supervisor, etc.
            }
        }
    }

    post {
        always {
            // Clean up or notify
            echo 'Pipeline completed.'
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
                echo 'Building the application...'
                // For example, if client has build process, but since it's vanilla JS, maybe not needed
            }
        }

        stage('Test') {
            steps {
                // Run tests if you have them
                echo 'Running tests...'
                // sh 'cd server && python3 -m pytest'  // If you add tests later
            }
        }

        stage('Deploy') {
            steps {
                // Deploy the application
                bat 'echo Deploying the application...'
                // Stop any existing process
                bat 'taskkill /F /IM python.exe /FI "WINDOWTITLE eq python app.py" || echo No process found'
                // Start the new application
                bat 'cd server && start cmd /c "python app.py > app.log 2>&1"'
                // Or use a process manager like systemd, supervisor, etc.
>>>>>>> c8ad168 (Remove Docker components and convert server to Python Flask, add Jenkins pipeline)
            }
        }
    }

    post {
<<<<<<< HEAD
        success {
            echo 'Deploy de PlusZone exitoso'
        }
        failure {
            echo 'Pipeline fallido - revisar logs'
        }
    }
}
=======
        always {
            // Clean up or notify
            echo 'Pipeline completed.'
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
>>>>>>> c8ad168 (Remove Docker components and convert server to Python Flask, add Jenkins pipeline)
