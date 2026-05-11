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
                bat '''
                    setlocal enabledelayedexpansion
                    set CHANGES=0
                    for /f %%i in ('git diff --name-only HEAD~1 2^>nul') do (
                        if (echo %%i | findstr "Jenkinsfile" >nul) (set CHANGES=1)
                        if (echo %%i | findstr "server" >nul) (set CHANGES=1)
                    )
                    call if !CHANGES! equ 1 (
                        echo "Changes detected in server/ or Jenkinsfile. Deploying..."
                        REM Matar solo el proceso Python que escucha en el puerto 4000
                        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":4000"') do (
                            taskkill /PID %%a /F /T 2>nul || exit /b 0
                        )
                        REM Esperar a que se libere el puerto
                        timeout /t 2 /nobreak
                        REM Iniciar el servidor Flask en background
                        cd server && start /B python app.py 1>> app.log 2>&1
                        REM Esperar a que el servidor inicie
                        timeout /t 5 /nobreak
                        REM Validar que el servidor está escuchando en puerto 4000
                        netstat -ano | findstr ":4000" | findstr "LISTENING" >nul
                        if errorlevel 1 (
                            echo ERROR: Servidor no inicio correctamente. Verificar logs.
                            exit /b 1
                        )
                        echo EXITO: Servidor iniciado correctamente en puerto 4000
                    ) else (
                        echo "No changes in server/ or Jenkinsfile, server continues running without restart"
                    )
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
