# Deploy en OCI Compute — NeoBank Alura RAG

Guia operativa para publicar la app Streamlit en una instancia **OCI Compute** (Always Free compatible) y obtener la IP publica.

**Shape por defecto:** `VM.Standard.A1.Flex` (Ampere, 1 OCPU / 6 GB) + **Canonical Ubuntu 22.04**.  
Si A1 no tiene capacidad: `VM.Standard.E2.1.Micro` (x86 Always Free).

La app lee `LLM_API_KEY` (Groq OpenAI-compatible). El script de deploy tambien escribe `GROQ_API_KEY` con el mismo valor.

---

## 0. Antes de desplegar

1. Asegurate de que GitHub tiene el codigo mas reciente:
   `https://github.com/FelipeOctavio87/Challenge_AluraAgent`
2. Ten a mano tu API key de Groq (`gsk_...`).
3. En tu PC, ten una clave SSH (si no existe):

```powershell
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa -N ""
```

- Publica: `%USERPROFILE%\.ssh\id_rsa.pub` (se sube a OCI)
- Privada: `%USERPROFILE%\.ssh\id_rsa` (nunca a GitHub)

---

## 1. Crear instancia Compute (consola OCI)

1. Entra a [Oracle Cloud Console](https://cloud.oracle.com/).
2. Menu hamburguesa → **Compute** → **Instances** → **Create instance**.
3. **Name:** `neobank-alura-rag`.
4. **Placement:** cualquier Availability Domain disponible (ej. AD-1).
5. **Image and shape** → **Edit**:
   - **Image:** Canonical Ubuntu 22.04 (Minimal o Standard).
   - **Shape:** `VM.Standard.A1.Flex` → 1 OCPU, 6 GB RAM (Always Free).
6. **Primary VNIC / Networking**:
   - VCN por defecto o Create new VCN.
   - Subnet **Public**.
   - **Assign a public IPv4 address:** Yes.
7. **Add SSH keys** → **Paste public keys** → pega el contenido de `id_rsa.pub`.
8. **Create** → espera estado **Running**.
9. En el detalle de la instancia, copia la **Public IP address**.

### Conexion SSH

Usuario Ubuntu en OCI: `ubuntu`.

```bash
ssh -i ~/.ssh/id_rsa ubuntu@<IP_PUBLICA>
```

En Windows (PowerShell):

```powershell
ssh -i $env:USERPROFILE\.ssh\id_rsa ubuntu@<IP_PUBLICA>
```

---

## 2. Abrir puerto 8501 (Security List / Ingress)

Ruta exacta en la consola:

1. Abre la instancia `neobank-alura-rag`.
2. Pestana **Networking** → clic en el nombre de la **Subnet** (o en la **VCN**).
3. En la subnet/VCN → **Security Lists**.
4. Entra a la lista asociada (suele llamarse `Default Security List for <vcn>`).
5. **Add Ingress Rules** → **+ Another Ingress Rule**:
   - **Source Type:** CIDR
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** TCP
   - **Destination Port Range:** `8501`
   - **Description:** `Streamlit NeoBank`
6. **Add Ingress Rules**.

Deja la regla de SSH (`22`) existente. Idealmente restringe `22` a tu IP publica.

---

## 3. Despliegue por SSH (script unico)

Conectado a la VM:

```bash
# Opcion A: clonar y ejecutar el script del repo
git clone https://github.com/FelipeOctavio87/Challenge_AluraAgent.git
cd Challenge_AluraAgent
# Edita GROQ_KEY dentro del script o exportala:
export GROQ_KEY="gsk_tu_clave_aqui"
bash scripts/deploy_oci.sh
```

Opcion B: pegar el contenido de [`scripts/deploy_oci.sh`](../scripts/deploy_oci.sh) en la sesion SSH (sustituyendo la key).

El script hace:

1. `apt` update + git + ufw
2. Instala Docker Engine + Compose plugin
3. Abre UFW: `22` y `8501`
4. Clona/actualiza el repo
5. Crea `.env` con `LLM_API_KEY`, `GROQ_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`
6. `sudo docker compose up -d --build`

### Verificar

```text
http://<IP_PUBLICA>:8501
```

Logs:

```bash
cd ~/Challenge_AluraAgent
sudo docker compose ps
sudo docker compose logs -f
```

---

## 4. Actualizar documentacion del repo

En `README.md` seccion **Enlace en vivo**, sustituye:

```text
http://<IP_PUBLICA_OCI>:8501
```

por tu IP real, por ejemplo:

```text
http://132.145.xx.xx:8501
```

Capturas (formato Markdown):

```markdown
![Pantalla inicial](docs/screenshots/01_home.png)
![Consulta SPEI](docs/screenshots/02_consulta_spei.png)
![Deploy OCI](docs/screenshots/03_oci_deploy.png)
```

---

## 5. Actualizar el contenedor mas adelante

```bash
cd ~/Challenge_AluraAgent
git pull
sudo docker compose up -d --build
```

---

## Notas

- **Nunca** subas `.env` ni API keys a GitHub.
- La primera build puede tardar **10–20+ minutos** en Always Free (descarga de torch/embeddings + indice FAISS).
- En la misma sesion SSH tras `usermod -aG docker`, usa `sudo docker ...` o cierra sesion y vuelve a entrar.
- Si la VM se queda sin RAM, prueba E2.1.Micro con menos carga o prebuild en otra maquina.
