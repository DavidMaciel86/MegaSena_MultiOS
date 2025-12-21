# storage.py
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from platformdirs import user_data_dir

APP_NAME = "MegaSurpresinhas"
APP_AUTHOR = "DavidMaciel_SmartSolutions"


def obter_pasta_historico() -> Path:
    base = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    pasta = base / "historico"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def salvar_historico_json(
    surpresinhas: List[List[int]],
    qtd_dezenas: int,
    qtd_surpresinhas: int,
    seed: Optional[int] = None,
) -> Path:
    pasta = obter_pasta_historico()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = pasta / f"surpresinhas_{timestamp}.json"

    payload: Dict[str, Any] = {
        "meta": {
            "criado_em": datetime.now().isoformat(timespec="seconds"),
            "seed": seed,
            "qtd_surpresinhas": qtd_surpresinhas,
            "qtd_dezenas": qtd_dezenas,
        },
        "surpresinhas": surpresinhas,
    }

    arquivo.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


def listar_historicos() -> List[Path]:
    pasta = obter_pasta_historico()
    return sorted(pasta.glob("surpresinhas_*.json"), reverse=True)


def ler_historico(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))
