# Optimización del Jenkinsfile - Resolución del Problema de Reinicio del Servidor

## Resumen Ejecutivo

Se ha corregido un problema crítico en el pipeline de CI/CD donde el servidor Python se reiniciaba innecesariamente en cada push, incluso cuando los cambios no afectaban el código del servidor. Esto provocaba interrupciones del servicio y errores de conexión.

## Problema Original

### Síntomas Observados

1. El servidor Python se caía después de cada push a cualquier rama
2. Las conexiones TCP mostraban estado `SYN_SENT` sin procesos en `LISTENING`
3. Acceso a la aplicación web fallaba con errores de conexión
4. El pipeline de Jenkins ejecutaba `taskkill /F /IM python.exe` indiscriminadamente

### Causa Raíz

El stage `Deploy` del Jenkinsfile ejecutaba el siguiente comando sin restricciones:

```batch
taskkill /F /IM python.exe /T
```

Este comando mataba todos los procesos Python en la máquina, incluyendo:
- El servidor Flask en puerto 4000 (proceso crítico)
- Cualquier otro proceso Python en ejecución

El problema se agravaba porque se ejecutaba en cada push, sin importar qué archivos se modificaran.

## Solución Implementada

### Cambios Realizados en el Jenkinsfile

#### 1. Condición de Ejecución Selectiva

Se agregó un bloque `when` al stage `Deploy`:

```groovy
stage('Deploy') {
    when {
        changeset pattern: "(server/.*|Jenkinsfile)"
    }
    steps {
        // Deploy solo ocurre si hay cambios en server/ o Jenkinsfile
    }
}
```

**Beneficio:** El stage Deploy ahora solo se ejecuta cuando hay cambios que realmente afectan el servidor.

#### 2. Identificación Específica del Proceso

Se reemplazó el comando global de terminación con una búsqueda específica:

```batch
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":4000"') do (
    taskkill /PID %%a /F /T 2>nul || exit /b 0
)
```

**Flujo:**
1. Ejecuta `netstat -ano` para listar todas las conexiones
2. Filtra solo las que escuchan en puerto 4000
3. Extrae el PID (identificador de proceso) del resultado
4. Mata solo ese proceso específico
5. Si no hay proceso en el puerto, continúa sin error

**Beneficio:** Únicamente termina el servidor Flask, sin afectar otros procesos.

#### 3. Tiempo de Espera para Liberación de Puerto

Se agregó una pausa antes de reiniciar:

```batch
timeout /t 2 /nobreak
```

**Beneficio:** Permite que el puerto se libere completamente, evitando errores de "puerto en uso".

## Impacto en el Flujo de Trabajo

### Escenarios y Comportamiento Resultante

| Tipo de Push | Comportamiento | Resultado |
|---|---|---|
| Push a `server/app.py` | Deploy se ejecuta, servidor se reinicia | Servidor actualizado, cambios aplicados |
| Push a `server/requirements.txt` | Deploy se ejecuta, dependencias se instalan | Servidor reinicia con nuevas dependencias |
| Push a `Jenkinsfile` | Deploy se ejecuta con nueva configuración | Cambios del pipeline aplicados |
| Push a `enlaces` (archivo de texto) | Pipeline corre, Deploy se salta | Servidor sigue corriendo sin interrupción |
| Push a `DOCUMENTACION.md` | Pipeline corre, Deploy se salta | Servidor sigue corriendo sin interrupción |
| Push a `docs/` o `client/` | Pipeline corre, Deploy se salta | Servidor sigue corriendo sin interrupción |

## Ventajas de la Solución

1. **Disponibilidad:** El servidor no se reinicia por cambios no relacionados
2. **Eficiencia:** El pipeline no ejecuta pasos innecesarios
3. **Precisión:** Solo se termina el proceso Flask específico
4. **Robustez:** Maneja casos donde el puerto no está en uso
5. **Escalabilidad:** Si en el futuro se ejecutan múltiples procesos Python, solo se afecta el del servidor

## Pruebas Recomendadas

### Prueba 1: Push sin cambios relevantes

```bash
# Editar un archivo que no está en el patrón
echo "Nueva línea" >> enlaces

# Hacer commit y push
git add enlaces
git commit -m "test: Cambio en archivo de documentación"
git push origin main
```

**Resultado esperado:** Pipeline corre pero Deploy se salta, servidor sigue activo.

### Prueba 2: Push con cambios en servidor

```bash
# Modificar el servidor
echo "# Nueva funcionalidad" >> server/app.py

# Hacer commit y push
git add server/app.py
git commit -m "feat: Nueva funcionalidad en servidor"
git push origin main
```

**Resultado esperado:** Pipeline corre, Deploy se ejecuta, servidor se reinicia correctamente.

### Prueba 3: Verificación de conectividad

```bash
# Verificar que el servidor está escuchando
netstat -ano | findstr :4000

# Verificar acceso a la aplicación web
curl http://localhost:4000
```

## Monitoreo Post-Despliegue

Se recomienda monitorear:

1. **Logs de Jenkins:** Verificar que el stage Deploy se ejecuta solo cuando corresponde
2. **Netstat:** Confirmar que el puerto 4000 está en estado `LISTENING`
3. **Logs de la aplicación:** Revisar `server/app.log` en busca de errores
4. **Acceso web:** Validar que la aplicación responde correctamente

## Archivos Modificados

- `Jenkinsfile` - Commit: `cf7536f`

## Referencias

- Patrón de cambios en Jenkins: https://www.jenkins.io/doc/declarative-pipeline/syntax/#changeset
- Comando netstat en Windows: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat
- Comando taskkill en Windows: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill
