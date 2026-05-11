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
                changeset pattern: "(server/.*|Jenkinsfile)"
            }
            steps {
                echo 'Detectados cambios en server/ o Jenkinsfile. Desplegando...'
                // Matar solo el proceso Python que escucha en el puerto 4000
                bat '''
                    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":4000"') do (
                        taskkill /PID %%a /F /T 2>nul || exit /b 0
                    )
                '''
                // Esperar a que se libere el puerto
                bat 'timeout /t 2 /nobreak'
                // Iniciar el servidor Flask en background
                bat 'cd server && start /B python app.py 1>> app.log 2>&1'
                // Esperar a que el servidor inicie
                bat 'timeout /t 3 /nobreak'
                // Validar que el servidor está escuchando en puerto 4000
                bat '''
                    netstat -ano | findstr ":4000" | findstr "LISTENING" >nul
                    if errorlevel 1 (
                        echo ERROR: Servidor no inicio correctamente. Verificar logs.
                        exit /b 1
                    )
                    echo EXITO: Servidor iniciado correctamente en puerto 4000
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
