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

from core import gerar_surpresinhas, preparar_pool_com_globo_com_status
from storage import (
    obter_pasta_historico,
    listar_historicos,
    ler_historico,
    salvar_historico_json,
)

from core_lotofacil import (
    preparar_pool_lotofacil_com_status,
    gerar_surpresinhas_lotofacil,
)

app = Flask(__name__)


@app.get("/sw.js")
def service_worker():
    resp = make_response(send_from_directory("static/js", "sw.js"))
    resp.headers["Content-Type"] = "application/javascript"
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

  <title>{{ titulo or "MegaSurpresinhas Mega-Sena" }}</title>

  <style>
  :root{
    --bg: #ffffff;
    --text: #111111;
    --muted: #555555;
    --border: #dddddd;
    --box-bg: #ffffff;
    --pre-bg: #f7f7f7;
    --btn-bg: #ffffff;
    --btn-text: #111111;
    --btn-border: #cccccc;
    --pill-bg: #ffffff;
  }

  /* Quando o usuário escolher dark */
  [data-theme="dark"]{
    --bg: #0f1115;
    --text: #e8e8e8;
    --muted: #b8b8b8;
    --border: #2a2f3a;
    --box-bg: #131722;
    --pre-bg: #0b0e14;
    --btn-bg: #1c2230;
    --btn-text: #e8e8e8;
    --btn-border: #2a2f3a;
    --pill-bg: #131722;
  }

  body {
    font-family: Arial, sans-serif;
    margin: 18px;
    background: var(--bg);
    color: var(--text);
    padding-bottom: 30px; /* garante espaço pra não “colar” no final */
  }

  .box {
    padding: 12px;
    border: 1px solid var(--border);
    background: var(--box-bg);
    border-radius: 10px;
    margin-bottom: 14px;
  }

  .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: end; }
  label { display: flex; flex-direction: column; gap: 6px; }

  input, select {
    padding: 8px;
    min-width: 180px;
    background: var(--box-bg);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
  }

  button {
    padding: 10px 14px;
    cursor: pointer;
    background: var(--btn-bg);
    color: var(--btn-text);
    border: 1px solid var(--btn-border);
    border-radius: 8px;
  }

  pre {
    background: var(--pre-bg);
    padding: 10px;
    border-radius: 10px;
    overflow: auto;
    border: 1px solid var(--border);
  }

  a { text-decoration: none; color: inherit; }
  a:hover { text-decoration: underline; }

  .small { color: var(--muted); font-size: 12px; }

  .pill {
    display:inline-block;
    padding:4px 8px;
    border:1px solid var(--border);
    border-radius:999px;
    margin:2px;
    background: var(--pill-bg);
  }

  /* Botão de tema no topo */
  .topbar{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:12px;
  }

  .theme-btn{
    display:flex;
    align-items:center;
    gap:8px;
    font-size:12px;
  }

  /* ✅ Resultado gerado: layout vertical + grupos de 3 */
  .resultado-lista{
    margin-top: 10px;
  }

  .linha-jogo{
    margin: 4px 0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
                 "Liberation Mono", "Courier New", monospace;
    white-space: nowrap;
  }

  .quebra-grupo{
    height: 10px; /* "pula uma linha" visual a cada 3 jogos */
  }

  /* ===== Histórico local em layout vertical ===== */
  .historico-item{
    display: block;
    padding: 10px;
    margin: 10px 0;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--box-bg);
  }

  /* ===== Navegação entre jogos ===== */
  .nav-game{
    flex:1;
    text-align:center;
    padding:10px;
    border:1px solid var(--border);
    border-radius:10px;
    background: var(--box-bg);
    font-weight:bold;
  }

  .nav-game.active{
    background: var(--btn-bg);
    border-color: var(--btn-border);
    box-shadow: inset 0 0 0 2px var(--btn-border);
  }

  /* ===== Lotofácil: layout em grade 5×N ===== */
  .lotofacil-grid{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
    margin-top: 6px;
  }

  .lotofacil-num{
    text-align: center;
    padding: 6px 0;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--pre-bg);
    font-weight: bold;
  }

  /* ================================
     Créditos no rodapé
  ================================ */
  .creditos{
    margin-top: 18px;
    padding: 10px 0 14px;
    text-align: center;
    font-size: 13px;
    opacity: 0.85;
  }
  </style>

</head>
<body>
  <div class="topbar">
    <h2 style="margin:0;">{{ titulo or "MegaSurpresinhas Mega-Sena" }}</h2>

    <button type="button" class="theme-btn" onclick="toggleTheme()">
      <span id="theme-icon">🌙</span>
      <span id="theme-label">Modo escuro</span>
    </button>
  </div>

  <div class="box" style="display:flex; gap:10px;">
    <a href="/" class="nav-game {{ 'active' if jogo_nome != 'lotofacil' else '' }}">
      Mega-Sena
    </a>

    <a href="/lotofacil" class="nav-game {{ 'active' if jogo_nome == 'lotofacil' else '' }}">
      Lotofácil
    </a>
  </div>

  <div class="box">
    <form method="post" action="{{ form_action or url_for('gerar') }}">
      <div class="row">

        <label>Qtd. surpresinhas (1–12)
          <input type="number" name="qtd_surpresinhas" min="1" max="12" value="{{ qtd_surpresinhas }}">
        </label>

        <label>Qtd. dezenas (6–12)
          <input type="number" name="qtd_dezenas"
                 min="{{ range_min_dezenas or 6 }}"
                 max="{{ range_max_dezenas or 12 }}"
                 value="{{ qtd_dezenas }}">
        </label>

        <button type="submit">Gerar</button>
      </div>
    </form>

    <p class="small">
      Pasta do histórico: <b>{{ pasta_historico }}</b>
    </p>
  </div>

  <!-- ✅ STATUS DE ORIGEM DOS DADOS -->
  {% if msg_status %}
    <div class="box small">
      <b>Modo:</b> {{ modo }} —
      <b>Fonte:</b>
      {% if fonte == "api_alt" %}
        Internet (API alternativa)
      {% elif fonte == "cache" %}
        Cache local
      {% elif fonte == "estatistico" %}
        Estatístico (1–60)
      {% else %}
        —
      {% endif %}
      <br>
      {{ msg_status }}
    </div>
  {% endif %}

  {% if erro %}
    <div class="box"><b>Erro:</b> {{ erro }}</div>
  {% endif %}

  {% if resultado %}
    <div class="box">
      <b>Resultado gerado:</b>

      <div class="resultado-lista">
        {% for jogo in resultado %}
          <div class="linha-jogo">
            {{ loop.index }}) {% for n in jogo %}{{ "%02d"|format(n) }}{% if not loop.last %} - {% endif %}{% endfor %}
          </div>

          {% if loop.index % 3 == 0 and not loop.last %}
            <div class="quebra-grupo"></div>
          {% endif %}
        {% endfor %}
      </div>

      <div class="small">Histórico salvo em: <b>{{ caminho_salvo }}</b></div>
    </div>
  {% endif %}

  <div class="box">
    <b>Histórico neste dispositivo:</b>

    <div id="historico-local" data-jogo="{{ jogo_nome or 'mega' }}" style="margin-top: 8px;"></div>

    <button
      type="button"
      style="margin-top: 10px;"
      onclick="handleLimparHistorico()"
    >
      Limpar histórico
    </button>

    <div class="small" style="margin-top: 6px;">
      O histórico é salvo apenas neste dispositivo.
    </div>
  </div>

  <script src="/static/js/app.js"></script>

  {% if resultado %}
  <script>
    (function () {
      if (typeof salvarHistorico !== "function" || typeof renderHistorico !== "function") {
        console.warn("Histórico: funções não carregadas (app.js).");
        return;
      }

      salvarHistorico({
        data: new Date().toLocaleString(),
        jogo: "{{ jogo_nome or 'mega' }}",
        modo: "{{ modo }}",
        fonte: "{{ fonte }}",
        jogos: {{ resultado | tojson }}
      });

      renderHistorico();
    })();
  </script>
  {% endif %}

  <script>
    document.addEventListener("DOMContentLoaded", () => {
      if (typeof renderHistorico === "function") {
        renderHistorico();
      }
    });
  </script>

  <footer class="creditos">
    By David Maciel
  </footer>
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
        qtd_surpresinhas=3,
        qtd_dezenas=6,
        pasta_historico=pasta,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=None,
        erro=None,
        modo=None,
        msg_status=None,
        fonte=None,
        jogo_nome="mega",
    )


@app.get("/lotofacil")
def lotofacil_index():
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]

    return render_template_string(
        HTML,
        # defaults da Lotofácil
        qtd_surpresinhas=3,  # quantidade de jogos
        qtd_dezenas=15,  # Lotofácil: 15–20
        pasta_historico=pasta,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=None,
        erro=None,
        modo=None,
        msg_status=None,
        fonte=None,
        # 👇 dica: usamos isso para o form apontar para /lotofacil/gerar
        jogo_nome="lotofacil",
        form_action=url_for("lotofacil_gerar"),
        titulo="MegaSurpresinhas Lotofácil",
        range_min_dezenas=15,
        range_max_dezenas=20,
    )


@app.post("/lotofacil/gerar")
def lotofacil_gerar():
    qtd_surpresinhas = _parse_int(request.form.get("qtd_surpresinhas", "3"), 3)
    qtd_dezenas = _parse_int(request.form.get("qtd_dezenas", "15"), 15)

    # validações específicas Lotofácil
    if not (1 <= qtd_surpresinhas <= 12):
        return _render_erro_lotofacil(
            "Qtd. de surpresinhas deve ser entre 1 e 12.",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    if not (15 <= qtd_dezenas <= 20):
        return _render_erro_lotofacil(
            "Qtd. de dezenas da Lotofácil deve ser entre 15 e 20.",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    try:
        pool, modo, fonte, msg_status = preparar_pool_lotofacil_com_status()
        surpresinhas = gerar_surpresinhas_lotofacil(
            qtd_surpresinhas,
            qtd_dezenas,
            pool,
        )

        caminho = salvar_historico_json(
            surpresinhas=surpresinhas,
            qtd_dezenas=qtd_dezenas,
            qtd_surpresinhas=qtd_surpresinhas,
        )

    except (requests.exceptions.RequestException, RuntimeError):
        return _render_erro_lotofacil(
            "Falha ao acessar os resultados oficiais da Lotofácil. Verifique sua conexão.",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    except ValueError as e:
        return _render_erro_lotofacil(
            f"Erro de validação dos dados: {e}",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    except Exception as e:
        return _render_erro_lotofacil(
            f"Erro inesperado ao gerar as surpresinhas: {e}",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]

    return render_template_string(
        HTML,
        qtd_surpresinhas=qtd_surpresinhas,
        qtd_dezenas=qtd_dezenas,
        pasta_historico=pasta,
        resultado=surpresinhas,
        caminho_salvo=str(caminho),
        historicos=historicos,
        historico_detalhe=None,
        erro=None,
        modo=modo,
        msg_status=msg_status,
        fonte=fonte,
        jogo_nome="lotofacil",
        form_action=url_for("lotofacil_gerar"),
        titulo="MegaSurpresinhas Lotofácil",
        range_min_dezenas=15,
        range_max_dezenas=20,
    )


def _render_erro_lotofacil(msg: str, qtd_surpresinhas: int, qtd_dezenas: int):
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]

    return render_template_string(
        HTML,
        qtd_surpresinhas=qtd_surpresinhas,
        qtd_dezenas=qtd_dezenas,
        pasta_historico=pasta,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=None,
        erro=msg,
        modo=None,
        msg_status=None,
        fonte=None,
        jogo_nome="lotofacil",
        form_action=url_for("lotofacil_gerar"),
        titulo="MegaSurpresinhas Lotofácil",
        range_min_dezenas=15,
        range_max_dezenas=20,
    )


@app.post("/gerar")
def gerar():
    qtd_surpresinhas = _parse_int(request.form.get("qtd_surpresinhas", "3"), 3)
    qtd_dezenas = _parse_int(request.form.get("qtd_dezenas", "6"), 6)

    # validações
    if not (1 <= qtd_surpresinhas <= 12):
        return _render_erro(
            "Qtd. de surpresinhas deve ser entre 1 e 12.",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    if not (6 <= qtd_dezenas <= 12):
        return _render_erro(
            "Qtd. de dezenas deve ser entre 6 e 12.",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    try:
        pool, modo, fonte, msg_status = preparar_pool_com_globo_com_status()
        surpresinhas = gerar_surpresinhas(qtd_surpresinhas, qtd_dezenas, pool)

        caminho = salvar_historico_json(
            surpresinhas=surpresinhas,
            qtd_dezenas=qtd_dezenas,
            qtd_surpresinhas=qtd_surpresinhas,
        )

    except (requests.exceptions.RequestException, RuntimeError):
        return _render_erro(
            "Falha ao acessar os resultados oficiais da Mega-Sena. Verifique sua conexão.",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    except ValueError as e:
        return _render_erro(
            f"Erro de validação dos dados: {e}",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    except Exception as e:
        return _render_erro(
            f"Erro inesperado ao gerar as surpresinhas: {e}",
            qtd_surpresinhas,
            qtd_dezenas,
        )

    # sucesso
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]

    return render_template_string(
        HTML,
        qtd_surpresinhas=qtd_surpresinhas,
        qtd_dezenas=qtd_dezenas,
        pasta_historico=pasta,
        resultado=surpresinhas,
        caminho_salvo=str(caminho),
        historicos=historicos,
        historico_detalhe=None,
        erro=None,
        modo=modo,
        msg_status=msg_status,
        fonte=fonte,
        jogo_nome="mega",
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
        qtd_surpresinhas=3,
        qtd_dezenas=6,
        pasta_historico=pasta_str,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=data,
        erro=None,
        modo=None,
        msg_status=None,
        fonte=None,
        jogo_nome="mega",
    )


def _render_erro(msg: str, qtd_surpresinhas: int, qtd_dezenas: int):
    pasta = str(obter_pasta_historico())
    historicos = listar_historicos()[:10]
    return render_template_string(
        HTML,
        qtd_surpresinhas=qtd_surpresinhas,
        qtd_dezenas=qtd_dezenas,
        pasta_historico=pasta,
        resultado=None,
        caminho_salvo=None,
        historicos=historicos,
        historico_detalhe=None,
        erro=msg,
        modo=None,
        msg_status=None,
        fonte=None,
        jogo_nome="mega",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
