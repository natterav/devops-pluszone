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
            when {
                anyOf {
                    changeset "server/**"
                    changeset "Jenkinsfile"
                }
            }
            steps {
                echo 'Desplegando servidor...'

                // Matar proceso en puerto 4000 solo si existe
                bat '''
                    netstat -ano | findstr ":4000" | findstr "LISTENING" >nul 2>&1
                    if not errorlevel 1 (
                        for /F "tokens=5" %%a in ('netstat -ano ^| findstr ":4000" ^| findstr "LISTENING"') do (
                            taskkill /PID %%a /F /T >nul 2>&1
                        )
                        ping localhost -n 3 >nul
                    )
                '''

                // Arrancar el servidor Flask en segundo plano
                bat 'cd server && start /B python app.py 1>> app.log 2>&1'

                // Esperar a que Flask inicialice
                bat 'ping localhost -n 5 >nul'

                // Validar que el servidor esta escuchando
                bat '''
                    netstat -ano | findstr ":4000" | findstr "LISTENING" >nul 2>&1
                    if errorlevel 1 (
                        echo ERROR: Servidor no inicio correctamente.
                        type app.log
                        exit /b 1
                    )
                    echo EXITO: Servidor corriendo en puerto 4000
                '''
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