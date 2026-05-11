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
                echo 'Paso 1: Deteniendo proceso anterior si existe...'
                bat 'taskkill /F /IM python.exe /T >nul 2>&1 & exit /b 0'

                echo 'Paso 2: Esperando que el puerto quede libre...'
                bat 'ping localhost -n 4 >nul'

                echo 'Paso 3: Arrancando servidor Flask...'
                bat 'cd server && start /B python app.py 1>> app.log 2>&1'

                echo 'Paso 4: Esperando inicializacion de Flask...'
                bat 'ping localhost -n 6 >nul'

                echo 'Paso 5: Verificando que el servidor responde...'
                bat '''
                    netstat -ano | findstr ":4000" | findstr "LISTENING" >nul 2>&1
                    if errorlevel 1 (
                        echo ERROR: El servidor no levanto. Contenido del log:
                        type server\\app.log
                        exit /b 1
                    )
                    echo EXITO: Servidor corriendo en http://localhost:4000
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
