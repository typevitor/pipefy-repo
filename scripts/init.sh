#!/bin/bash
set -e

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Arquivo .env criado a partir do .env.example."
  echo "Preencha as variáveis obrigatórias antes de continuar."
  exit 1
fi

docker compose up -d --build
