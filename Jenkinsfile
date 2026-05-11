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
                bat 'cd server && powershell -Command "Start-Process python -ArgumentList app.py -NoNewWindow -RedirectStandardOutput app.log -RedirectStandardError app.log"'
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
                // Verificar que el servidor responde a requests HTTP
                bat 'powershell -Command "try { $response = Invoke-WebRequest -Uri http://localhost:4000 -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host \"EXITO: Servidor responde correctamente\" } else { Write-Host \"ERROR: Servidor no responde con 200\"; exit 1 } } catch { Write-Host \"ERROR: No se puede conectar al servidor: $_\"; exit 1 }"'
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
