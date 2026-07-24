# Ejemplos de preguntas y respuestas esperadas

Casos de demo para validar el agente RAG de NeoBank Alura.

| Pregunta | Respuesta esperada (idea clave) | Fuente tipica |
|----------|----------------------------------|---------------|
| Cual es la comision por transferencia SPEI saliente? | 8.00 MXN por operacion | tarifas_comisiones.pdf / tarifas.csv |
| Como activo el 2FA? | App > Configuracion > Seguridad > Activar 2FA > escanear QR | seguridad_fraude.pdf |
| Cuales son los limites SPEI diarios? | Hasta 100,000 MXN diarios en nivel completo | politicas_cuenta.pdf |
| Que hago si sospecho robo de credenciales? | Bloquear cuenta, restablecer contrasena, rotar 2FA, revisar movimientos | seguridad_fraude.pdf |
| Cuanto cuesta la reposicion de tarjeta debit? | 80.00 MXN | tarifas.csv / tarifas_comisiones.pdf |
| Hay mensualidad de mantenimiento? | No, si hay al menos una operacion en 12 meses | tarifas_comisiones.pdf |
| Cual es el email de privacidad? | privacidad@neobank-alura.example | terminos_condiciones.pdf |

## Capturas

Coloca capturas de la UI Streamlit en esta carpeta (`docs/screenshots/`) tras probar en local o en OCI, por ejemplo:

- `01_home.png` — pantalla inicial
- `02_consulta_spei.png` — respuesta con fuentes
- `03_oci_deploy.png` — app abierta con la IP publica
