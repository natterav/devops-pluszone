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
                        echo %%i | findstr /r "server/\\|Jenkinsfile" >nul && set CHANGES=1
                    )
                    if !CHANGES!==1 (
                        echo "Changes detected in server/ or Jenkinsfile. Deploying..."
                        REM Matar solo el proceso Python que escucha en el puerto 4000
                        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":4000"') do (
                            taskkill /PID %%a /F /T 2>nul || exit /b 0
                        )
                        REM Esperar a que se libere el puerto
                        timeout /t 2 /nobreak
                        REM Iniciar el servidor Flask en background
                        cd server && powershell -Command "Start-Process python -ArgumentList app.py -NoNewWindow -RedirectStandardOutput app.log -RedirectStandardError app.log"
                        REM Esperar a que el servidor inicie
                        timeout /t 5 /nobreak
                        REM Validar que el servidor está escuchando en puerto 4000
                        netstat -ano | findstr ":4000" | findstr "LISTENING" >nul
                        if errorlevel 1 (
                            echo ERROR: Servidor no inicio correctamente. Verificar logs.
                            exit /b 1
                        )
                        echo EXITO: Servidor iniciado correctamente en puerto 4000
                        REM Verificar que el servidor responde a requests HTTP
                        powershell -Command "try { $response = Invoke-WebRequest -Uri http://localhost:4000 -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host \"EXITO: Servidor responde correctamente\" } else { Write-Host \"ERROR: Servidor no responde con 200\"; exit 1 } } catch { Write-Host \"ERROR: No se puede conectar al servidor: $_\"; exit 1 }"
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
