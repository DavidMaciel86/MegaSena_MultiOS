from __future__ import annotations

import requests

from flask import (
    Flask,
    request,
    render_template_string,
    redirect,
    url_for,
    send_from_directory,
    make_response,
)

from core import aplicar_seed, gerar_surpresinhas, preparar_pool_com_globo
from storage import (
    obter_pasta_historico,
    listar_historicos,
    ler_historico,
    salvar_historico_json,
)

app = Flask(__name__)


@app.get("/sw.js")
def service_worker():
    resp = make_response(send_from_directory("static/js", "sw.js"))
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/manifest.webmanifest")
def manifest():
    # Se o arquivo estiver na raiz do projeto, este caminho está correto.
    # Se você moveu o manifest para /static, troque "." por "static".
    resp = make_response(send_from_directory(".", "manifest.webmanifest"))
    resp.headers["Content-Type"] = "application/manifest+json"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


HTML = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <link rel="manifest" href="/static/manifest.webmanifest">
  <meta name="theme-color" content="#111111">

  <title>MegaSurpresinhas (Web)</title>

  <style>
    body { font-family: Arial, sans-serif; margin: 18px; }
    .box { padding: 12px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 14px; }
    .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: end; }
    label { display: flex; flex-direction: column; gap: 6px; }
    input, select { padding: 8px; min-width: 180px; }
    button { padding: 10px 14px; cursor: pointer; }
    pre { background:#f7f7f7; padding:10px; border-radius:10px; overflow:auto; }
    a { text-decoration: none; }
    .small { color:#555; font-size: 12px; }
    .pill { display:inline-block; padding:4px 8px; border:1px solid #ddd; border-radius:999px; margin:2px; }
  </style>
</head>
<body>
  <h2>MegaSurpresinhas (Interface Web)</h2>

  <div class="box">
    <form method="post" action="{{ url_for('gerar') }}">
      <div class="row">
        <label>Seed (opcional)
          <input type="number" name="seed" placeholder="ENTER = aleatório" value="{{ seed or '' }}">
        </label>

        <label>Qtd. surpresinhas (1–12)
          <input type="number" name="qtd_surpresinhas" min="1" max="12" value="{{ qtd_surpresinhas }}">
        </label>

        <label>Qtd. dezenas (6–12)
          <input type="number" name="qtd_dezenas" min="6" max="12" value="{{ qtd_dezenas }}">
        </label>

        <button type="submit">Gerar e salvar histórico</button>
      </div>
    </form>

    <p class="small">
      <b>Seed utilizada:</b>
      {% if seed is not none and seed != "" %}
        {{ seed }}
      {% else %}
        aleatória
      {% endif %}
    </p>

    <p class="small">
      Pasta do histórico: <b>{{ pasta_historico }}</b>
    </p>
  </div>

  {% if erro %}
    <div class="box"><b>Erro:</b> {{ erro }}</div>
  {% endif %}

  {% if resultado %}
    <div class="box">
      <b>Resultado gerado:</b>
      <pre>{{ resultado }}</pre>
      <div class="small">Histórico salvo em: <b>{{ caminho_salvo }}</b></div>
    </div>
  {% endif %}

  <div class="box">
    <b>Últimos históricos:</b>
    {% if historicos %}
      <div style="margin-top: 8px;">
        {% for item in historicos %}
          <div style="margin: 6px 0;">
            <span class="pill">{{ loop.index }}</span>
            <a href="{{ url_for('ver_historico', nome=item.name) }}">{{ item.name }}</a>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <div class="small">Nenhum histórico salvo ainda.</div>
    {% endif %}
  </div>

  {% if historico_detalhe %}
    <div class="box">
      <b>Detalhe do histórico:</b>
      <pre>{{ historico_detalhe }}</pre>
    </div>
  {% endif %}

  <script src="/static/js/app.js"></script>

</body>
</html>
"""


def _parse_int(value: str, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default


@app.get("/")
def index():
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]
    return render_template_string(
        HTML,
        seed=None,
        qtd_surpresinhas=3,
        qtd_dezenas=6,
        pasta_historico=pasta,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=None,
        erro=None,
    )


@app.post("/gerar")
def gerar():
    seed_raw = request.form.get("seed", "").strip()
    seed = _parse_int(seed_raw, default=0) if seed_raw else None

    qtd_surpresinhas = _parse_int(request.form.get("qtd_surpresinhas", "3"), 3)
    qtd_dezenas = _parse_int(request.form.get("qtd_dezenas", "6"), 6)

    # validações
    if not (1 <= qtd_surpresinhas <= 12):
        return _render_erro(
            "Qtd. de surpresinhas deve ser entre 1 e 12.",
            seed_raw,
            qtd_surpresinhas,
            qtd_dezenas,
        )
    if not (6 <= qtd_dezenas <= 12):
        return _render_erro(
            "Qtd. de dezenas deve ser entre 6 e 12.",
            seed_raw,
            qtd_surpresinhas,
            qtd_dezenas,
        )

    try:
        aplicar_seed(seed)
        pool = preparar_pool_com_globo()
        surpresinhas = gerar_surpresinhas(qtd_surpresinhas, qtd_dezenas, pool)

        caminho = salvar_historico_json(
            surpresinhas=surpresinhas,
            qtd_dezenas=qtd_dezenas,
            qtd_surpresinhas=qtd_surpresinhas,
            seed=seed,
        )

    # ⬇️ AQUI está a principal adaptação:
    except (requests.exceptions.RequestException, RuntimeError):
        # RequestException -> erro de rede / HTTP
        # RuntimeError (ou similar) -> erro ao processar dados oficiais
        return _render_erro(
            "Falha ao acessar os resultados oficiais da Mega-Sena. Verifique sua conexão.",
            seed_raw,
            qtd_surpresinhas,
            qtd_dezenas,
        )

    except ValueError as e:
        return _render_erro(
            f"Erro de validação dos dados: {e}",
            seed_raw,
            qtd_surpresinhas,
            qtd_dezenas,
        )

    except Exception as e:
        return _render_erro(
            f"Erro inesperado ao gerar as surpresinhas: {e}",
            seed_raw,
            qtd_surpresinhas,
            qtd_dezenas,
        )

    # sucesso
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]
    return render_template_string(
        HTML,
        seed=seed_raw,
        qtd_surpresinhas=qtd_surpresinhas,
        qtd_dezenas=qtd_dezenas,
        pasta_historico=pasta,
        resultado=surpresinhas,
        caminho_salvo=str(caminho),
        historicos=historicos,
        historico_detalhe=None,
        erro=None,
    )


@app.get("/historico/<nome>")
def ver_historico(nome: str):
    pasta = obter_pasta_historico()
    caminho = pasta / nome
    if not caminho.exists():
        return redirect(url_for("index"))

    data = ler_historico(caminho)

    pasta_str = str(pasta)
    historicos = listar_historicos()[:10]
    return render_template_string(
        HTML,
        seed=None,
        qtd_surpresinhas=3,
        qtd_dezenas=6,
        pasta_historico=pasta_str,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=data,
        erro=None,
    )


def _render_erro(msg: str, seed_raw: str, qtd_surpresinhas: int, qtd_dezenas: int):
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]
    return render_template_string(
        HTML,
        seed=seed_raw,
        qtd_surpresinhas=qtd_surpresinhas,
        qtd_dezenas=qtd_dezenas,
        pasta_historico=pasta,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=None,
        erro=msg,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

