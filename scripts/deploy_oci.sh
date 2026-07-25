#!/usr/bin/env bash
# Deploy NeoBank Alura RAG en Ubuntu (OCI Compute).
# Uso:
#   export GROQ_KEY="gsk_..."
#   bash scripts/deploy_oci.sh
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if [[ -z "${GROQ_KEY:-}" ]]; then
  echo "ERROR: define GROQ_KEY antes de ejecutar."
  echo "  export GROQ_KEY=\"gsk_tu_clave\""
  exit 1
fi

REPO_URL="https://github.com/FelipeOctavio87/Challenge_AluraAgent.git"
REPO_DIR="${HOME}/Challenge_AluraAgent"

echo "==> Actualizando paquetes base"
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg git ufw

echo "==> Instalando Docker Engine + Compose plugin"
sudo install -m 0755 -d /etc/apt/keyrings
if [[ ! -f /etc/apt/keyrings/docker.gpg ]]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker "${USER}" || true

echo "==> Firewall UFW (SSH + Streamlit 8501)"
sudo ufw allow OpenSSH
sudo ufw allow 8501/tcp
sudo ufw --force enable

echo "==> Clonando / actualizando repositorio"
if [[ -d "${REPO_DIR}/.git" ]]; then
  git -C "${REPO_DIR}" pull --ff-only
else
  git clone "${REPO_URL}" "${REPO_DIR}"
fi
cd "${REPO_DIR}"

echo "==> Creando .env de produccion"
cat > .env <<EOF
LLM_API_KEY=${GROQ_KEY}
GROQ_API_KEY=${GROQ_KEY}
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K=4
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EOF
chmod 600 .env

echo "==> Levantando contenedor (puede tardar varios minutos la primera vez)"
sudo docker compose up -d --build

PUBLIC_IP="$(curl -fsS ifconfig.me || true)"
echo ""
echo "Deploy listo."
if [[ -n "${PUBLIC_IP}" ]]; then
  echo "URL: http://${PUBLIC_IP}:8501"
else
  echo "URL: http://<IP_PUBLICA_OCI>:8501"
fi
sudo docker compose ps
sudo docker compose logs --tail=50
