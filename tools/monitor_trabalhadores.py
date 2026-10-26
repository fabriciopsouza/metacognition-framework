#!/usr/bin/env python3
"""monitor_trabalhadores.py — trilha de auditoria e monitor da orquestracao (ADR-131).

Le a trilha `~/.claude/estado/trabalhadores/registro.jsonl` (uma linha por etapa) e gera UMA
pagina HTML autonoma, sem servidor, sem rede e sem dependencia: indicadores, consumo por
trabalhador e a linha do tempo de cada trabalho, com o resumo da resposta e o link para a
integra. O executor (`trabalhador_externo.py`) regera a pagina a cada chamada; as etapas feitas
dentro do Claude Code (autor, QA, merge) entram na mesma trilha pelo subcomando `evento`.

Nada aqui chama modelo: custo zero de token. O nome e o objetivo de cada trabalho vem do
registro de trabalhos (ADR-100, `tools/trabalhos.py`), sem copia.

Uso:
  python tools/monitor_trabalhadores.py gerar [--abrir]
  python tools/monitor_trabalhadores.py texto [--ultimas 20]
  python tools/monitor_trabalhadores.py evento --trabalho <slug> --etapa "<rotulo>" --quem "<papel e modelo>"
         --status OK|FALHOU|EM-CURSO|RECUSADO|ERRO|INVALIDO [--resumo "..."] [--spec <caminho>] [--repo <nome>]
"""
import argparse
import datetime as _dt
import html
import json
import os
import sys
from collections import OrderedDict, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STATUS = ("OK", "EM-CURSO", "FALHOU", "RECUSADO", "ERRO", "INVALIDO")
RUINS = {"FALHOU", "RECUSADO", "ERRO", "INVALIDO"}


def registro_path():
    return os.environ.get("TRABALHADOR_REGISTRO") or os.path.join(
        os.path.expanduser("~"), ".claude", "estado", "trabalhadores", "registro.jsonl")


def ler(caminho=None):
    caminho = caminho or registro_path()
    linhas, ruins = [], 0
    # Eventos "status ..." gravados em 25/10/2026 para desenhar o plano na trilha: o plano agora vem de
    # painel.json, e esses eventos nao sao etapas; ficam fora da contagem (registro append-only, nao se apaga).
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    d = json.loads(ln)
                except ValueError:
                    d = None
                if not isinstance(d, dict):
                    ruins += 1  # linha corrompida e' contada e mostrada, nunca ignorada em silencio
                    continue
                # [QA r1 Q5] JSON valido fora do formato nao pode derrubar a pagina inteira
                for k in TEXTO:
                    if k in d and d[k] is not None and not isinstance(d[k], str):
                        d[k] = str(d[k])
                if not d.get("status"):
                    d["status"] = "?"
                if (str(d.get("quem", "")).endswith("(status)") and str(d.get("etapa", "")).startswith("status ")
                        and str(d.get("quando", "")).startswith("2026-10-25")):
                    continue
                linhas.append(d)
    return linhas, ruins


TEXTO = ("quando", "trabalho", "etapa", "quem", "trabalhador", "modelo", "familia", "via", "repo",
         "classe", "status", "resumo", "spec", "saida", "id")


def _info_trabalho(slug):
    try:
        import trabalhos
        d = trabalhos._ler(trabalhos._caminho(slug))
    except Exception:
        d = None
    if not d:
        return {"nome": slug, "objetivo": "", "status": "", "arquivo": None}
    fm = d.get("fm", {})
    return {"nome": fm.get("trabalho") or slug, "objetivo": fm.get("objetivo", ""),
            "status": fm.get("status", ""), "arquivo": d.get("caminho")}


def _uri(caminho):
    """[QA r1 Q7/Q8] link so para arquivo que existe, com codificacao correta (#, espaco, acento)."""
    if not caminho or not os.path.isfile(caminho):
        return None
    from pathlib import Path
    return Path(caminho).resolve().as_uri()


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


VIAS_FORA = ("agy", "ollama", "codex")


def _fora(ln):
    """Etapa executada fora do Claude: via externa, ou Codex registrado como evento do Claude Code."""
    quem = (ln.get("trabalhador") or ln.get("quem") or "").lower()
    return ln.get("via") in VIAS_FORA or quem.startswith("codex")


def agregar(linhas):
    tot = {"etapas": len(linhas), "ok": 0, "ruins": 0, "em_curso": 0, "tok_in": 0, "tok_out": 0, "seg": 0.0,
           "poupado": 0, "fora": 0, "fora_sem_medida": 0}
    por_trab = defaultdict(lambda: {"chamadas": 0, "tok_in": 0, "tok_out": 0, "ruins": 0, "familia": "", "via": "",
                                    "fora": False, "sem_medida": 0, "poupado": 0})
    trabalhos = OrderedDict()
    # EM-CURSO so conta se for o registro mais recente daquela etapa: o fecho posterior o substitui
    ultimo = {}
    for i, ln in enumerate(linhas):
        ultimo[(ln.get("trabalho"), ln.get("etapa"))] = i
    for i, ln in enumerate(linhas):
        st = ln.get("status", "")
        tot["ok"] += st == "OK"
        tot["ruins"] += st in RUINS
        tot["em_curso"] += st == "EM-CURSO" and ultimo.get((ln.get("trabalho"), ln.get("etapa"))) == i
        tot["tok_in"] += _num(ln.get("tokens_entrada"))
        tot["tok_out"] += _num(ln.get("tokens_saida"))
        tot["seg"] += _num(ln.get("segundos"))
        quem = ln.get("trabalhador") or ln.get("quem") or "?"
        p = por_trab[quem]
        p["chamadas"] += 1
        p["tok_in"] += _num(ln.get("tokens_entrada"))
        p["tok_out"] += _num(ln.get("tokens_saida"))
        p["ruins"] += st in RUINS
        p["familia"] = ln.get("familia") or p["familia"]
        p["via"] = ln.get("via") or p["via"]
        if _fora(ln):
            p["fora"] = True
        # conta etapa concluida (OK), nao linha: o EM-CURSO de abertura e o fecho OK da mesma etapa contam uma vez
        if _fora(ln) and st == "OK":
            # economia bruta: o que a IA externa processou e o Claude deixou de processar (ADR-131)
            medido = ln.get("tokens_entrada") is not None or ln.get("tokens_saida") is not None
            tot["fora"] += 1
            if medido:
                n = _num(ln.get("tokens_entrada")) + _num(ln.get("tokens_saida"))
                tot["poupado"] += n
                p["poupado"] += n  # a linha do trabalhador usa a mesma regra do card
            else:
                tot["fora_sem_medida"] += 1
                p["sem_medida"] += 1
        trabalhos.setdefault(ln.get("trabalho") or "-", []).append(ln)
    return tot, dict(por_trab), trabalhos


def _fmt(n):
    return f"{n:,.0f}".replace(",", ".")


CSS = """
:root{--bg:#0b0f17;--bg2:#121826;--card:#161e2e;--line:#253049;--tx:#e6ebf5;--mut:#8b97b0;
--ok:#3ddc97;--bad:#ff6b6b;--run:#ffc857;--acc:#7aa2ff;--acc2:#c084fc;--chip:#1d2740}
@media (prefers-color-scheme: light){:root:not([data-tema="escuro"]){--bg:#f4f6fb;--bg2:#e9eef7;--card:#fff;
--line:#d6dceb;--tx:#121826;--mut:#5b6680;--ok:#0f9d63;--bad:#d64045;--run:#b7791f;--acc:#3d63dd;--acc2:#8b3fd9;--chip:#eef2fb}}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(1200px 600px at 10% -10%,color-mix(in srgb,var(--acc) 18%,transparent),transparent),
radial-gradient(900px 500px at 110% 0%,color-mix(in srgb,var(--acc2) 14%,transparent),transparent),var(--bg);
color:var(--tx);font:14px/1.45 "Segoe UI",system-ui,sans-serif;min-height:100vh}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 64px}
header{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;justify-content:space-between;margin-bottom:20px}
h1{margin:0;font-size:26px;letter-spacing:-.02em}h1 span{background:linear-gradient(90deg,var(--acc),var(--acc2));
-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--mut);font-size:13px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px;position:relative;overflow:hidden}
.kpi:after{content:"";position:absolute;inset:auto 0 0 0;height:3px;background:var(--k,var(--acc))}
.kpi b{display:block;font-size:26px;letter-spacing:-.02em}.kpi small{color:var(--mut)}
.painel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin-bottom:18px}
.painel h2{margin:0 0 12px;font-size:15px}
.barra{display:grid;grid-template-columns:150px 1fr 150px;gap:10px;align-items:center;margin:8px 0;font-size:13px}
.trilho{height:10px;background:var(--chip);border-radius:99px;overflow:hidden}
.trilho i{display:block;height:100%;background:linear-gradient(90deg,var(--acc),var(--acc2));border-radius:99px}
.ferr{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.ferr input{flex:1;min-width:200px;background:var(--card);border:1px solid var(--line);color:var(--tx);border-radius:10px;padding:9px 12px;font:inherit}
.ferr button{background:var(--chip);border:1px solid var(--line);color:var(--tx);border-radius:99px;padding:7px 12px;font:inherit;cursor:pointer}
.ferr button[aria-pressed=true]{background:var(--acc);border-color:var(--acc);color:#fff}
.trab{background:var(--card);border:1px solid var(--line);border-radius:16px;margin-bottom:16px;overflow:hidden}
.trab>summary{list-style:none;cursor:pointer;padding:14px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}
.trab>summary::-webkit-details-marker{display:none}
.trab h3{margin:0;font-size:16px}.obj{color:var(--mut);font-size:13px;margin-top:2px}
.mini{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-size:12px;padding:3px 9px;border-radius:99px;background:var(--chip);border:1px solid var(--line);white-space:nowrap}
.st-OK{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 45%,transparent)}
.st-RUIM{color:var(--bad);border-color:color-mix(in srgb,var(--bad) 45%,transparent)}
.st-EM-CURSO{color:var(--run);border-color:color-mix(in srgb,var(--run) 45%,transparent)}
ol.tl{list-style:none;margin:0;padding:4px 16px 16px 34px;position:relative}
ol.tl:before{content:"";position:absolute;left:21px;top:8px;bottom:22px;width:2px;background:var(--line)}
ol.tl li{position:relative;padding:10px 12px;margin:8px 0;border-radius:12px;background:var(--bg2);border:1px solid var(--line)}
ol.tl li:before{content:"";position:absolute;left:-19px;top:16px;width:10px;height:10px;border-radius:50%;background:var(--d,var(--acc));
box-shadow:0 0 0 4px color-mix(in srgb,var(--d,var(--acc)) 25%,transparent)}
.cab{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between}
.cab strong{font-size:14px}.meta{color:var(--mut);font-size:12px}
.res{margin-top:6px;font-size:13px;word-break:break-word}
a{color:var(--acc)}.vazio{color:var(--mut);text-align:center;padding:40px}
.alerta{border-color:var(--bad);color:var(--bad)}
.kpi small+b+small{display:block;margin-top:2px}
.secao{font-size:15px;margin:22px 0 10px}
.tab{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em;
padding:8px;border-bottom:1px solid var(--line)}td{padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td .trilho{height:6px;margin-top:4px;min-width:60px}td code{font-size:12px;word-break:break-word}
.grupos{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.g{background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.duas{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:18px}.duas .painel{margin-bottom:18px}
.painel p{margin:6px 0}.painel ul{margin:6px 0;padding-left:20px}details.painel>summary{cursor:pointer}
@media (max-width:640px){.barra{grid-template-columns:1fr}.kpi b{font-size:22px}}
"""

JS = """
const q=document.getElementById('q'),bs=[...document.querySelectorAll('.ferr button')];
function aplicar(){const t=(q.value||'').toLowerCase(),f=(bs.find(b=>b.getAttribute('aria-pressed')==='true')||{}).dataset||{};
document.querySelectorAll('ol.tl li').forEach(li=>{const ok=(!t||li.textContent.toLowerCase().includes(t))&&(!f.f||f.f==='todos'||li.dataset.g===f.f);li.hidden=!ok});
document.querySelectorAll('.trab').forEach(d=>{d.hidden=![...d.querySelectorAll('li')].some(li=>!li.hidden)});
try{sessionStorage.setItem('mon',JSON.stringify({t:q.value,f:f.f||'todos',open:[...document.querySelectorAll('.trab[open]')].map(d=>d.id)}))}catch(e){}}
bs.forEach(b=>b.onclick=()=>{bs.forEach(x=>x.setAttribute('aria-pressed','false'));b.setAttribute('aria-pressed','true');aplicar()});
q.oninput=aplicar;document.querySelectorAll('.trab').forEach(d=>d.ontoggle=aplicar);
try{const s=JSON.parse(sessionStorage.getItem('mon')||'{}');if(s.t)q.value=s.t;if(s.f)bs.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.f===s.f)));
if(s.open)s.open.forEach(id=>{const d=document.getElementById(id);if(d)d.open=true})}catch(e){}
aplicar();setTimeout(()=>location.reload(),20000);
"""


def _grupo(st):
    return "ok" if st == "OK" else ("curso" if st == "EM-CURSO" else "ruim")


def _cor(st):
    return "var(--ok)" if st == "OK" else ("var(--run)" if st == "EM-CURSO" else "var(--bad)")


def _cls(st):
    return "st-OK" if st == "OK" else ("st-EM-CURSO" if st == "EM-CURSO" else "st-RUIM")


def html_pagina(linhas, ruins=0, painel=None, erro_painel=None):
    """Ordem pedida pelo dono (25/10/2026): cards de entrega, cards da trilha, plano (blocos, grupos, agora, com o
    dono), linha do tempo das etapas e, por último, consumo por trabalhador."""
    e = html.escape
    tot, por_trab, trabalhos = agregar(linhas)
    agora = _dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    titulo = str(painel.get("titulo") or "") if painel else ""
    titulo = titulo or "Trilha da orquestração"
    meta_plano = f"{e(str(painel.get('meta')))} · " if painel and painel.get("meta") else ""
    p = [f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>{e(titulo)}</title><style>{CSS}</style></head><body><div class='wrap'>"
         f"<header><div><h1><span>{e(titulo)}</span></h1><div class='sub'>{meta_plano}Cada etapa, quem executou, o resultado e o custo. "
         f"Atualizado em {e(agora)} · recarrega a cada 20 s</div></div>"
         f"<div class='sub'>Fonte: {e(registro_path())}</div></header>"]
    if ruins:
        p.append(f"<div class='painel alerta'>{ruins} linha(s) corrompida(s) na trilha foram ignoradas na contagem.</div>")
    if erro_painel:
        p.append(f"<div class='painel alerta'>Plano do painel ilegível ({e(erro_painel)}); mostrando só a trilha.</div>")
    topo, corpo = "", ""
    if painel:
        try:
            topo, corpo = html_plano(painel)
        except Exception as ex:  # plano fora do formato nunca derruba a pagina da trilha
            p.append(f"<div class='painel alerta'>Plano do painel fora do formato ({e(type(ex).__name__)}); "
                     "mostrando só a trilha.</div>")
    nota = (f"economia bruta: o que IAs externas processaram em {tot['fora']} etapa(s); o custo do Claude para "
            "preparar e ler não é descontado")
    if tot["fora_sem_medida"]:
        nota += f"; {tot['fora_sem_medida']} etapa(s) sem medição"
    poupado = (f"<div class='kpi' style='--k:var(--ok)'><small>Tokens processados fora do Claude</small>"
               f"<b>{_fmt(tot['poupado'])}</b><small>{e(nota)}</small></div>")
    # o card fica na primeira linha: junto das entregas, ou abrindo a linha da trilha quando nao ha plano
    p.append(topo.replace("<section class='kpis'>", "<section class='kpis'>" + poupado, 1) if topo else "")
    kp = [("Etapas", _fmt(tot["etapas"]), "var(--acc)"), ("Concluídas", _fmt(tot["ok"]), "var(--ok)"),
          ("Com problema", _fmt(tot["ruins"]), "var(--bad)"), ("Em curso", _fmt(tot["em_curso"]), "var(--run)"),
          ("Tokens enviados (só etapas medidas)", _fmt(tot["tok_in"]), "var(--acc2)"),
          ("Tokens recebidos (só etapas medidas)", _fmt(tot["tok_out"]), "var(--acc2)")]
    p.append("<section class='kpis'>" + ("" if topo else poupado) + "".join(
        f"<div class='kpi' style='--k:{c}'><small>{e(n)}</small><b>{v}</b></div>" for n, v, c in kp) + "</section>")
    p.append(corpo)
    p.append("<h2 class='secao'>Etapas por trabalho</h2>")
    p.append("<div class='ferr'><input id='q' type='search' placeholder='Filtrar por trabalho, etapa, modelo, texto da resposta' aria-label='Filtrar'>"
             "<button data-f='todos' aria-pressed='true'>Todas</button><button data-f='ok' aria-pressed='false'>Concluídas</button>"
             "<button data-f='ruim' aria-pressed='false'>Com problema</button><button data-f='curso' aria-pressed='false'>Em curso</button></div>")
    if not trabalhos:
        p.append("<div class='painel vazio'>Nenhuma etapa registrada ainda. A trilha começa na primeira chamada do executor "
                 "ou no primeiro <code>evento</code>.</div>")
    for i, (slug, etapas) in enumerate(reversed(list(trabalhos.items()))):
        info = _info_trabalho(slug) if slug != "-" else {"nome": "Sem trabalho declarado", "objetivo": "", "status": "", "arquivo": None}
        ult = etapas[-1]
        n_ruins = sum(x.get("status") in RUINS for x in etapas)
        specs = sorted({x.get("spec") for x in etapas if x.get("spec")})
        mini = [f"<span class='chip {_cls(ult.get('status', ''))}'>última: {e(ult.get('status', '?'))}</span>",
                f"<span class='chip'>{len(etapas)} etapa(s)</span>"]
        if n_ruins:
            mini.append(f"<span class='chip st-RUIM'>{n_ruins} com problema</span>")
        mini.append(f"<span class='chip'>{e(str(ult.get('quando', ''))[:16].replace('T', ' '))}</span>")
        p.append(f"<details class='trab' id='t{i}' {'open' if i == 0 else ''}><summary><div><h3>{e(info['nome'])}</h3>"
                 f"<div class='obj'>{e(info['objetivo'] or slug)}"
                 + (f" · <a href='{e(_uri(info['arquivo']))}'>registro do trabalho</a>" if _uri(info["arquivo"]) else "")
                 + "".join((f" · spec <a href='{e(_uri(s))}'>{e(os.path.basename(s))}</a>" if _uri(s)
                            else f" · spec {e(s)}") for s in specs)
                 + f"</div></div><div class='mini'>{''.join(mini)}</div></summary><ol class='tl'>")
        for x in reversed(etapas):
            st = x.get("status", "?")
            quem = x.get("quem") or " · ".join(v for v in (x.get("trabalhador"), x.get("modelo")) if v)
            via = x.get("via") or "claude-code"
            meta = [str(x.get("quando", ""))[:19].replace("T", " "), f"via {via}"]
            if x.get("repo"):
                meta.append(f"repo {x['repo']} ({x.get('classe', '?')})")
            if x.get("segundos") is not None:
                meta.append(f"{x['segundos']} s")
            if x.get("tokens_entrada") is not None:
                meta.append(f"{_fmt(_num(x.get('tokens_entrada')))} → {_fmt(_num(x.get('tokens_saida')))} tokens")
            link = f" · <a href='{e(_uri(x['saida']))}'>íntegra</a>" if _uri(x.get("saida")) else ""
            p.append(f"<li data-g='{_grupo(st)}' style='--d:{_cor(st)}'><div class='cab'><strong>{e(x.get('etapa') or '-')}</strong>"
                     f"<span class='chip {_cls(st)}'>{e(st)}</span></div>"
                     f"<div class='meta'>{e(quem)} · {e(' · '.join(meta))}{link}</div>"
                     + (f"<div class='res'>{e(x['resumo'])}</div>" if x.get("resumo") else "") + "</li>")
        p.append("</ol></details>")
    if por_trab:
        maior = max(x["tok_in"] + x["tok_out"] for x in por_trab.values()) or 1
        p.append("<section class='painel'><h2>Consumo por trabalhador</h2>")
        for nome, x in sorted(por_trab.items(), key=lambda kv: -(kv[1]["tok_in"] + kv[1]["tok_out"])):
            w = round(100 * (x["tok_in"] + x["tok_out"]) / maior)
            onde = "fora do Claude Code" if x["fora"] else ("portão de dado" if x["via"] == "portao" else "Claude Code")
            poup = ""
            if x["fora"]:
                poup = f" · {_fmt(x['poupado'])} processados fora do Claude (etapas OK)"
                if x["sem_medida"]:
                    poup += f" · {x['sem_medida']} sem medição"
            p.append(f"<div class='barra'><div><strong>{e(nome)}</strong><div class='meta'>{e(onde)}</div></div>"
                     f"<div class='trilho' role='img' aria-label='{w}% do maior consumo'><i style='width:{max(w, 2)}%'></i></div>"
                     f"<div class='meta'>{x['chamadas']} etapa(s) · {_fmt(x['tok_in'] + x['tok_out'])} tokens"
                     f"{' · ' + str(x['ruins']) + ' com problema' if x['ruins'] else ''}{e(poup)}</div></div>")
        p.append("</section>")
    p.append(f"</div><script>{JS}</script></body></html>")
    return "".join(p)


def painel_path(caminho_registro=None):
    return os.environ.get("TRABALHADOR_PAINEL") or os.path.join(
        os.path.dirname(caminho_registro or registro_path()), "painel.json")


def ler_painel(caminho=None):
    """Plano do status, opcional. Devolve (dados, erro): sem arquivo -> (None, None); arquivo invalido ->
    (None, motivo), e a pagina avisa sem cair. Formato (todas as chaves opcionais):
      titulo, meta, onde, falta, proximo: texto
      entregas: [[rotulo, valor, nota], ...]            cards do topo
      blocos:   [[bloco, o que e, situacao, pct 0-100, onde esta, o que falta], ...]
                situacao: "ok" (concluido), "wip" (em andamento), "todo" (nao iniciado); outro valor = "todo"
      grupos:   [[grupo, situacao em texto], ...]
      comDono, fontes: [texto, ...]"""
    caminho = caminho or painel_path()
    if not os.path.exists(caminho):
        return None, None
    try:
        with open(caminho, encoding="utf-8-sig") as f:
            d = json.load(f)
    except (OSError, ValueError, RecursionError) as ex:
        return None, f"{type(ex).__name__}: {ex}"
    if not isinstance(d, dict):
        return None, "o painel tem de ser um objeto JSON"
    return d, None


def _lista(v):
    return [x for x in v if isinstance(x, (list, tuple))] if isinstance(v, list) else []


SIT = {"ok": ("concluído", "var(--ok)"), "wip": ("em andamento", "var(--run)"), "todo": ("não iniciado", "var(--mut)")}


def _pct(v):
    try:
        return max(0, min(100, round(float(v))))
    except (TypeError, ValueError, OverflowError):
        return 0


def html_plano(d):
    """Cards de entrega e blocos do plano; todo texto escapado."""
    e = lambda v: html.escape("" if v is None else str(v))  # noqa: E731
    cores = ("var(--ok)", "var(--run)", "var(--acc)", "var(--bad)", "var(--acc2)")
    cards = _lista(d.get("entregas"))
    topo = ""
    if cards:
        topo = "<section class='kpis'>" + "".join(
            f"<div class='kpi' style='--k:{cores[i % len(cores)]}'><small>{e(c[0] if len(c) > 0 else '')}</small>"
            f"<b>{e(c[1] if len(c) > 1 else '')}</b><small>{e(c[2] if len(c) > 2 else '')}</small></div>"
            for i, c in enumerate(cards)) + "</section>"
    corpo = []
    blocos = _lista(d.get("blocos"))
    if blocos:
        corpo.append("<section class='painel'><h2>Blocos do plano</h2><div class='tab'><table><thead><tr><th>Bloco</th>"
                     "<th>O que é</th><th>Situação</th><th>%</th><th>Onde está</th><th>O que falta</th></tr></thead><tbody>")
        for b in blocos:
            b = list(b) + [""] * (6 - len(b))
            nome, cor = SIT.get(b[2] if isinstance(b[2], str) else "", SIT["todo"])
            p = _pct(b[3])
            corpo.append(f"<tr><td><strong>{e(b[0])}</strong></td><td>{e(b[1])}</td>"
                         f"<td><span class='chip' style='color:{cor}'>{nome}</span></td>"
                         f"<td>{p}%<div class='trilho' aria-hidden='true'><i style='width:{p}%'></i></div></td>"
                         f"<td><code>{e(b[4])}</code></td><td>{e(b[5])}</td></tr>")
        corpo.append("</tbody></table></div></section>")
    grupos = _lista(d.get("grupos"))
    if grupos:
        corpo.append("<section class='painel'><h2>Entregas por grupo</h2><div class='grupos'>" + "".join(
            f"<div class='g'><strong>{e(g[0] if g else '')}</strong><div class='meta'>{e(g[1] if len(g) > 1 else '')}</div></div>"
            for g in grupos) + "</div></section>")
    agora = [(r, d.get(k)) for r, k in (("Onde estamos", "onde"), ("O que falta", "falta"), ("Próximo passo", "proximo"))
             if d.get(k)]
    dono = [x for x in d.get("comDono", []) if x] if isinstance(d.get("comDono"), list) else []
    if agora or dono:
        corpo.append("<section class='duas'>")
        if agora:
            corpo.append("<div class='painel'><h2>Agora</h2>" + "".join(
                f"<p><strong>{e(r)}:</strong> {e(v)}</p>" for r, v in agora) + "</div>")
        if dono:
            corpo.append("<div class='painel'><h2>Com o dono</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in dono)
                         + "</ul></div>")
        corpo.append("</section>")
    fontes = [x for x in d.get("fontes", []) if x] if isinstance(d.get("fontes"), list) else []
    if fontes:
        corpo.append("<details class='painel'><summary><strong>Fontes conferidas</strong></summary><ul>"
                     + "".join(f"<li>{e(x)}</li>" for x in fontes) + "</ul></details>")
    return topo, "".join(corpo)


def monitor_path(caminho_registro=None):
    return os.path.join(os.path.dirname(caminho_registro or registro_path()), "monitor.html")


def gerar(caminho_registro=None):
    linhas, ruins = ler(caminho_registro)
    painel, erro_painel = ler_painel(painel_path(caminho_registro))
    destino = monitor_path(caminho_registro)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    tmp = destino + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html_pagina(linhas, ruins, painel, erro_painel))
    os.replace(tmp, destino)  # troca atomica: o navegador nunca le pagina pela metade
    return destino


def evento(trabalho, etapa, quem, status, resumo=None, spec=None, repo=None):
    if status not in STATUS:
        raise ValueError(f"status '{status}' fora de {STATUS}")
    import trabalhador_externo as tx
    linha = {**tx._carimbo(), "trabalho": trabalho, "etapa": etapa, "quem": quem, "via": "claude-code",
             "status": status, "spec": spec, "repo": repo, "resumo": tx.resumir(resumo or "")}
    return tx.registrar({k: v for k, v in linha.items() if v not in (None, "")})


def texto(ultimas=20):
    linhas, ruins = ler()
    tot, _, _ = agregar(linhas)
    print(f"Etapas {tot['etapas']} · OK {tot['ok']} · problema {tot['ruins']} · em curso {tot['em_curso']} · "
          f"tokens {tot['tok_in']}->{tot['tok_out']}" + (f" · {ruins} linha(s) corrompida(s)" if ruins else ""))
    for x in linhas[-ultimas:]:
        quem = x.get("quem") or x.get("trabalhador") or "?"
        print(f"{str(x.get('quando', ''))[:16]}  {(x.get('status') or '?'):9} {(x.get('trabalho') or '-')[:22]:22} "
              f"{(x.get('etapa') or '-')[:28]:28} {quem[:24]:24} {(x.get('resumo') or '')[:60]}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monitor e trilha da orquestracao (ADR-131)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("--abrir", action="store_true")
    t = sub.add_parser("texto")
    t.add_argument("--ultimas", type=int, default=20)
    ev = sub.add_parser("evento")
    ev.add_argument("--trabalho", required=True)
    ev.add_argument("--etapa", required=True)
    ev.add_argument("--quem", required=True)
    ev.add_argument("--status", required=True, choices=STATUS)
    ev.add_argument("--resumo")
    ev.add_argument("--spec")
    ev.add_argument("--repo")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "gerar":
        destino = gerar()
        print(destino)
        if a.abrir and hasattr(os, "startfile"):
            os.startfile(destino)  # noqa: S606 — abre no navegador padrao (Windows)
        return 0
    if a.cmd == "texto":
        texto(a.ultimas)
        return 0
    print(evento(a.trabalho, a.etapa, a.quem, a.status, a.resumo, a.spec, a.repo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
