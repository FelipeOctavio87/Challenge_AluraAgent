# Deploy en OCI Compute — NeoBank Alura RAG

Guia simplificada para publicar la app Streamlit en una instancia **OCI Compute** (Always Free compatible).

## 1. Crear la instancia

1. Entra a [Oracle Cloud Console](https://cloud.oracle.com/).
2. **Compute → Instances → Create instance**.
3. Configuracion recomendada Always Free:
   - **Shape:** `VM.Standard.A1.Flex` (Ampere) o `VM.Standard.E2.1.Micro`
   - **Image:** Ubuntu 22.04
   - **Networking:** VCN con subnet **publica** y asignar IP publica
4. Sube tu **SSH public key**.
5. Crea la instancia y anota la **IP publica**.

## 2. Abrir el puerto de la app (Security List / NSG)

La app escucha en el puerto **8501**.

1. Ve a la VCN de la instancia → **Security Lists** (o Network Security Group).
2. Agrega regla **Ingress**:
   - Source: `0.0.0.0/0` (o tu IP si quieres restringir)
   - IP Protocol: TCP
   - Destination Port: `8501`
3. Mantén SSH (`22`) limitado a tu IP.

En la VM (Ubuntu), si usas UFW:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 8501/tcp
sudo ufw enable
```

## 3. Instalar Docker en la VM

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
# cierra sesion SSH y vuelve a entrar
```

## 4. Clonar y levantar la app

```bash
git clone https://github.com/FelipeOctavio87/Challenge_AluraAgent.git
cd Challenge_AluraAgent

# Crea .env con tu API key (Groq / OpenAI compatible)
cp .env.example .env
nano .env

docker build -t neobank-rag .
docker run -d --name neobank-rag -p 8501:8501 \
  --env-file .env \
  neobank-rag
```

Alternativa con Compose:

```bash
docker compose up -d --build
```

## 5. Verificar

Abre en el navegador:

```
http://<IP_PUBLICA_OCI>:8501
```

Logs:

```bash
docker logs -f neobank-rag
```

## 6. Actualizar

```bash
cd Challenge_AluraAgent
git pull
docker build -t neobank-rag .
docker rm -f neobank-rag
docker run -d --name neobank-rag -p 8501:8501 --env-file .env neobank-rag
```

## Notas

- **Nunca** subas `.env` ni API keys a GitHub.
- La primera build descarga el modelo de embeddings; puede tardar varios minutos en shapes micro.
- Si la VM se queda sin RAM, reduce dependencias o preconstruye el indice en otra maquina y monta `vectorstore/` como volumen.
- Documenta la IP publica final en el `README.md` del repositorio.
