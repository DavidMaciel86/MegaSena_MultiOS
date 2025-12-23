# core.py
from __future__ import annotations

import random
from typing import List, Optional

import requests

API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    # alguns servidores da Caixa gostam de ver esses cabeçalhos:
    "Origin": "https://loterias.caixa.gov.br",
    "Referer": "https://loterias.caixa.gov.br/",
}


def obter_ultimo_concurso() -> int:
    url = API_BASE
    response = requests.get(url, headers=COMMON_HEADERS, timeout=15)
    response.raise_for_status()
    dados = response.json()
    return int(dados["numero"])


def obter_concurso(numero_concurso: int) -> dict:
    url = f"{API_BASE}/{numero_concurso}"
    response = requests.get(url, headers=COMMON_HEADERS, timeout=15)
    response.raise_for_status()
    return response.json()


def coletar_ultimos_10_resultados() -> List[int]:
    ultimo_concurso = obter_ultimo_concurso()
    pool_dezenas: List[int] = []

    for concurso in range(ultimo_concurso, ultimo_concurso - 10, -1):
        dados_concurso = obter_concurso(concurso)
        lista_dezenas = dados_concurso["listaDezenas"]  # vem como strings
        dezenas_int = [int(d) for d in lista_dezenas]
        pool_dezenas.extend(dezenas_int)  # repetições contam mais no pool

    return pool_dezenas


def gerar_surpresinhas(
    qtd_surpresinhas: int,
    qtd_dezenas: int,
    pool_dezenas: List[int],
) -> List[List[int]]:
    surpresinhas: List[List[int]] = []

    for _ in range(qtd_surpresinhas):
        jogo: List[int] = []
        while len(jogo) < qtd_dezenas:
            numero = random.choice(pool_dezenas)
            if numero not in jogo:
                jogo.append(numero)

        jogo.sort()
        surpresinhas.append(jogo)

    return surpresinhas


def preparar_pool_com_globo() -> List[int]:
    pool = coletar_ultimos_10_resultados()
    pool.extend(range(1, 61))  # garante chance mínima p/ todas as dezenas
    return pool


def aplicar_seed(seed: Optional[int]) -> None:
    if seed is not None:
        random.seed(seed)