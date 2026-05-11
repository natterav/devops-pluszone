# Plan de Validación - Fixes del Jenkinsfile

## Verificación Actual (Estado Confirmado)

El servidor Flask está funcionando correctamente:

- Servidor escuchando en puerto 4000: CONFIRMED
- Status HTTP 200: CONFIRMED
- netstat mostrand LISTENING: CONFIRMED

## Plan de Pruebas Recomendado

### Prueba 1: Commit Innecesario (Sin cambios relevantes)

Objetivo: Verificar que el servidor NO se reinicia ante cambios no relacionados.

Pasos:

1. Abrir el archivo `enlaces` o `DOCUMENTACION.md`
2. Realizar un cambio menor (agregar un comentario)
3. Guardar, hacer commit y push
4. En Jenkins: Verificar que el pipeline corre
5. Verificar que el stage Deploy se SALTA (no se ejecuta)
6. Verificar que el servidor sigue en LISTENING

Comando para verificar:

```batch
netstat -ano | findstr ":4000"
```

Resultado esperado:

```
  TCP    0.0.0.0:4000     0.0.0.0:0         LISTENING       [PID]
```

---

### Prueba 2: Commit en Servidor (Cambios relevantes)

Objetivo: Verificar que el Deploy se ejecuta y valida correctamente.

Pasos:

1. Realizar cambio en `server/app.py` (agregar un comentario)
2. Hacer commit y push
3. En Jenkins: Monitor del build

Verificar que ocurra lo siguiente:

- Stage Deploy se EJECUTA
- Proceso anterior en puerto 4000 se mata
- Nueva instancia de Flask se inicia
- Validación POST-DEPLOY pasa (muestra: "EXITO: Servidor iniciado correctamente en puerto 4000")
- Pipeline finaliza con SUCCESS

Comando para verificar después del deploy:

```batch
netstat -ano | findstr ":4000"
python -c "import urllib.request; response = urllib.request.urlopen('http://localhost:4000'); print(f'Status: {response.status}')"
```

Resultado esperado:

```
  TCP    0.0.0.0:4000     0.0.0.0:0         LISTENING       [PID_NUEVO]
Status: 200
```

---

### Prueba 3: Acceso a la Aplicación Web

Objetivo: Verificar que la interfaz web está funcional después del deploy.

Pasos:

1. Abrir navegador
2. Ir a http://localhost:4000
3. Verificar que la página carga correctamente
4. Verificar que los assets (CSS, JS) cargan correctamente

---

### Prueba 4: Commit en Jenkinsfile

Objetivo: Verificar que cambios al Jenkinsfile disparan deploy.

Pasos:

1. Realizar cambio en `Jenkinsfile` (agregar comentario)
2. Hacer commit y push
3. En Jenkins: Verificar que Deploy se ejecuta

---

### Prueba 5: Múltiples Commits Consecutivos

Objetivo: Verificar estabilidad ante cambios rápidos.

Pasos:

1. Hacer 3 commits a archivos no relevantes:
   - Cambio 1: enlaces
   - Cambio 2: DOCUMENTACION.md
   - Cambio 3: README.md

2. Cada commit debería:
   - Ejecutar pipeline
   - SALTAR stage Deploy
   - Mantener servidor activo

3. Luego hacer 1 commit relevante:
   - Cambio en server/requirements.txt

4. Este commit debería:
   - Ejecutar pipeline
   - EJECUTAR stage Deploy
   - Reiniciar servidor

---

## Señales de Alerta

Detener las pruebas y revisar logs si:

- netstat muestra múltiples conexiones en SYN_SENT
- Status HTTP no es 200
- Jenkins muestra ERROR en stage Deploy
- Servidor responde 502 o 503
- app.log contiene errores

---

## Monitoreo en Tiempo Real

Mientras se ejecutan pruebas, ejecutar en terminal separada:

```batch
REM Monitorear cambios en puerto 4000 cada 2 segundos
:loop
cls
echo === Estado del Servidor [%date% %time%] ===
netstat -ano | findstr ":4000"
echo.
timeout /t 2 /nobreak
goto loop
```

---

## Logs Importantes

Revisar estos archivos después de cada prueba:

1. **Jenkins Console Output**: Ver ejecución del pipeline
   - URL: http://localhost:8080 (si Jenkins está en localhost)
   
2. **Server Logs**: `server/app.log`
   - Ver si hay errores al iniciar
   - Ver si hay excepciones durante ejecución

3. **Verification Debug Log**: `server/verification_debug.log`
   - Logs de email/verificación

---

## Criterios de Éxito

Todas las pruebas deben cumplir:

- [ ] Prueba 1: Deploy se salta, servidor sigue activo
- [ ] Prueba 2: Deploy se ejecuta, servidor reinicia exitosamente
- [ ] Prueba 3: Interfaz web carga correctamente
- [ ] Prueba 4: Jenkinsfile trigger funciona
- [ ] Prueba 5: Servidor es estable ante múltiples cambios
- [ ] No hay conexiones SYN_SENT después de deploy
- [ ] Respuestas HTTP son siempre 200 (cuando debería serlo)
