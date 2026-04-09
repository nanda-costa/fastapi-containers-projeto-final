#!/usr/bin/env bash
set -euo pipefail

show_title() {
  printf "\n\033[1;36m%s\033[0m\n" "$1"
}

run_command() {
  local command="$1"
  local description="$2"

  printf "\nComando   : \033[1m%s\033[0m\n" "$command"
  printf "Descrição : %s\n" "$description"
  read -r -p "Executar agora? [s/N] " confirm
  if [[ "$confirm" =~ ^[sS]$ ]]; then
    eval "$command"
  else
    printf "Operação cancelada.\n"
  fi
}

while true; do
  show_title "Menu Docker - Gestor PD&I Track"
  printf "\n[1]  Ciclo da Stack  - docker compose up -d --build\n"
  printf "[2]  Ciclo da Stack  - docker compose down\n"
  printf "[3]  Ciclo da Stack  - docker compose restart api\n"
  printf "[4]  Diagnóstico     - docker compose ps\n"
  printf "[5]  Diagnóstico     - docker compose logs -f api\n"
  printf "[6]  Diagnóstico     - docker compose logs postgres\n"
  printf "[7]  Depuração       - docker compose exec api sh\n"
  printf "[8]  Depuração       - docker compose exec postgres psql -U appuser -d appdb\n"
  printf "[9]  Depuração       - docker inspect projeto_api\n"
  printf "[10] Imagens/Build   - docker compose build --no-cache\n"
  printf "[11] Imagens/Build   - docker images\n"
  printf "[12] Imagens/Build   - docker system prune\n"
  printf "[0]  Sair\n"

  read -r -p "Escolha uma opção: " option

  case "$option" in
    1) run_command "docker compose up -d --build" "Sobe toda a stack e reconstrói as imagens." ;;
    2) run_command "docker compose down" "Para e remove os containers da stack." ;;
    3) run_command "docker compose restart api" "Reinicia somente o serviço da API." ;;
    4) run_command "docker compose ps" "Mostra o status de todos os serviços." ;;
    5) run_command "docker compose logs -f api" "Exibe os logs da API em tempo real." ;;
    6) run_command "docker compose logs postgres" "Exibe os logs do banco PostgreSQL." ;;
    7) run_command "docker compose exec api sh" "Abre um shell dentro do container da API." ;;
    8) run_command "docker compose exec postgres psql -U appuser -d appdb" "Abre o cliente psql dentro do container do banco." ;;
    9) run_command "docker inspect projeto_api" "Mostra os detalhes completos do container da API." ;;
    10) run_command "docker compose build --no-cache" "Reconstrói as imagens sem usar cache." ;;
    11) run_command "docker images" "Lista as imagens Docker disponíveis localmente." ;;
    12) run_command "docker system prune" "Remove recursos Docker não utilizados." ;;
    0) printf "Saindo...\n"; exit 0 ;;
    *) printf "Opção inválida.\n" ;;
  esac

done