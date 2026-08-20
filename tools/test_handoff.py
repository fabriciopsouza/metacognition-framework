#!/usr/bin/env python3
"""Canario do handoff.py (ADR-076): prova que o gerador (a) RODA e emite os 5 campos P14 + sugestao de
modelo, (b) a regra papel+risco mapeia corretamente, (c) e DETERMINISTICO (mesmos inputs -> mesma saida).
Sem (b)/(c) a "sugestao deterministica" seria prosa. Fail-closed.

Uso: python tools/test_handoff.py   (exit 0 PASS; 1 se falha)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import handoff  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P14_SECTIONS = [
    "[modelo sugerido]",
    "[P14] Artefato consumivel",
    "[P14] Localizacao",
    "[P14] Acesso",
    "[P14] Prompt pronto-para-colar",
    "[P14] Pendencias e premissas herdadas",
]

# (next_role, risk, author) -> familia esperada (ADR-078: politica lida de model-policy.json;
# tier max = fable [Mythos-class, acima de Opus], balanced = sonnet, economy = haiku)
MODEL_CASES = [
    ("qa-critic", "low", "opus", "sonnet"),   # heterogeneo: autor tier-alto -> sonnet
    ("qa-critic", "low", "fable", "sonnet"),  # heterogeneo: autor fable -> sonnet
    ("qa-critic", "low", "sonnet", "fable"),  # heterogeneo: autor sonnet -> tier max
    ("review", "low", "opus", "sonnet"),
    # DECISAO DO DONO 19/08/2026: coordenacao cross-IA saiu do tier max. Era a ultima porta que
    # abria o degrau acima do default POR PAPEL, sem autorizacao ativa. Devolver para "fable"
    # aqui reprova.
    ("cross-ai", "low", "opus", "opus"),      # handoff cross-IA -> baseline
    ("handoff gemini", "low", "opus", "opus"),
    # DECISAO DO DONO 18/08/2026: fable NAO e default. Arquiteto, planejador e executor sao OPUS;
    # fable entra so no SEGUNDO QA adversarial final (model-policy.json:qa_final_duplo). Se alguem
    # devolver esses papeis para o tier max, este canario reprova de novo.
    ("architect", "low", "opus", "opus"),
    ("discovery", "low", "opus", "opus"),
    ("docops", "low", "opus", "haiku"),       # tier economy (mecanico gateado por canario)
    ("developer", "low", "opus", "opus"),     # papel autoral -> tier baseline (= opus hoje; ADR-082)
    ("developer", "high", "opus", "fable"),   # risco sobrepoe papel -> tier max
    ("docops", "regulated", "sonnet", "fable"),  # risco sobrepoe papel
]

ROLE_CASES = [
    ("rodar o qa-critic adversarial no bloco", "qa-critic"),
    ("entregar handoff cross-IA para o gemini", "cross-ai"),
    ("decidir a arquitetura e abrir ADR", "architect"),
    ("implementar o script e o canario", "developer"),
    ("atualizar CHANGELOG e taggear o release", "docops"),
]


def main():
    fails = []
    # pre-condicao de ambiente (achado BAIXO do process-critic v1.57.0): MODEL_CASES assume
    # nenhuma indisponibilidade declarada — limpa env herdada (canario roda em processo proprio)
    os.environ.pop("FRAMEWORK_MODELS_UNAVAILABLE", None)

    # (a) roda e emite os campos
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "handoff.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        fails.append(f"handoff.py exit {r.returncode} (esperado 0)")
    out = r.stdout or ""
    for s in P14_SECTIONS:
        if s not in out:
            fails.append(f"saida sem secao P14: {s!r}")
    if "claude-" not in out:
        fails.append("saida sem ID de modelo sugerido (claude-*)")

    # (b) regra papel+risco
    for role, risk, author, expect_fam in MODEL_CASES:
        fam, _why = handoff.suggest_model(role, risk, author)
        if fam != expect_fam:
            fails.append(f"suggest_model({role},{risk},autor={author}) = {fam}, esperado {expect_fam}")
        if handoff.MODEL_ID.get(fam) is None:
            fails.append(f"familia {fam} sem ID em MODEL_ID")

    # (b2) inferencia de papel
    for text, expect_role in ROLE_CASES:
        got = handoff.infer_role(text)
        if got != expect_role:
            fails.append(f"infer_role({text!r}) = {got}, esperado {expect_role}")

    # (b3) schema da policy (ADR-078): fonte unica integra — tiers resolvem a model_ids,
    # roles apontam para tiers existentes, escada declarada, risk_override valido.
    pol = handoff.POLICY
    for key in ("model_ids", "tiers", "roles", "default_tier", "risk_override", "heterogeneity_ladder"):
        if key not in pol:
            fails.append(f"model-policy.json sem chave obrigatoria '{key}'")
    for tname, t in pol.get("tiers", {}).items():
        chain = t.get("chain") or []
        if not chain:
            fails.append(f"tier '{tname}' sem chain de fallback")
        for fam in chain:
            if fam not in pol.get("model_ids", {}):
                fails.append(f"tier '{tname}': familia '{fam}' na chain sem model_id")
    for rule in pol.get("roles", []):
        tr = rule.get("tier")
        if tr != "heterogeneous" and tr not in pol.get("tiers", {}):
            fails.append(f"role {rule.get('match')} aponta tier inexistente '{tr}'")
    if pol.get("default_tier") not in pol.get("tiers", {}):
        fails.append(f"default_tier '{pol.get('default_tier')}' inexistente")
    for rk, rv in pol.get("risk_override", {}).items():
        if not rk.startswith("_") and rv not in pol.get("tiers", {}):
            fails.append(f"risk_override['{rk}'] aponta tier inexistente '{rv}'")
    if len(pol.get("heterogeneity_ladder", [])) < 3:
        fails.append("heterogeneity_ladder incompleta (3 degraus: cross-IA > modelo!=, > fresh declarado)")

    # (b3.1) baseline_author (ADR-082): autor da SESSAO >= baseline; relativo/evolutivo, guardado por canario
    ba = pol.get("baseline_author")
    if not isinstance(ba, dict):
        fails.append("model-policy.json sem bloco 'baseline_author' (ADR-082)")
    else:
        bm = (ba.get("model") or "").lower()
        if bm not in pol.get("model_ids", {}):
            fails.append(f"baseline_author.model '{bm}' sem model_id correspondente")
        if "baseline" not in pol.get("tiers", {}):
            fails.append("baseline_author exige tier 'baseline' (autor roda nele)")
        elif pol["tiers"]["baseline"]["chain"][0].lower() != bm:
            fails.append(f"tier baseline.chain[0] '{pol['tiers']['baseline']['chain'][0]}' != baseline_author.model '{bm}' (devem coincidir)")
        if not ba.get("author_roles"):
            fails.append("baseline_author.author_roles vazio (quais papeis sao autorais)")
    # papel autoral developer DEVE resolver ao baseline (nao mais ao default balanced)
    # (b3.1) DECISAO DO DONO 18/08/2026: o QA adversarial final e DUPLO, sonnet depois fable, e a
    # politica tem de dizer isso como DADO. Sem esta assercao, apagar o bloco nao reprovaria nada.
    # A regra do dono e RELATIVA: executor no default, 1o QA um degrau abaixo, 2o QA um degrau acima.
    # A assercao e CALCULADA da escada — assim, promover o baseline move os dois criticos junto e este
    # canario continua verdadeiro sem ninguem reescrever numero nenhum.
    qfd = pol.get("qa_final_duplo")
    esc = (pol.get("escada_relativa") or {}).get("ordem")
    if not isinstance(esc, list) or len(esc) < 3:
        fails.append("model-policy.json sem 'escada_relativa.ordem' — a regra de QA e relativa ao "
                     "default e sem a escada ela nao pode ser resolvida")
    elif not isinstance(qfd, dict):
        fails.append("model-policy.json sem 'qa_final_duplo' — a decisao do dono de fechar bloco com "
                     "DOIS QA adversariais finais nao esta registrada como dado")
    else:
        base = (pol.get("baseline_author") or {}).get("model")
        # [qa-critic Sonnet 19/08/2026, achado ALTA] a assercao era TAUTOLOGICA: ela calculava o
        # esperado a partir da propria escada, entao inverter a ordem passava verde — com o critico
        # barato no degrau caro e vice-versa. A ordem passa a ser conferida contra os tiers, que sao
        # declaracao independente no mesmo arquivo: o topo do tier `max` e o mais capaz, e o topo do
        # tier `economy` e o mais barato.
        topo_max = ((pol.get("tiers") or {}).get("max") or {}).get("chain") or []
        topo_eco = ((pol.get("tiers") or {}).get("economy") or {}).get("chain") or []
        if topo_max and esc and topo_max[0] != esc[-1]:
            fails.append(f"escada_relativa.ordem termina em {esc[-1]!r}, mas o tier 'max' comeca em "
                         f"{topo_max[0]!r} — a ordem da escada contradiz os tiers do mesmo arquivo; "
                         f"invertida, ela poria o critico barato no degrau caro")
        if topo_eco and esc and topo_eco[0] != esc[0]:
            fails.append(f"escada_relativa.ordem comeca em {esc[0]!r}, mas o tier 'economy' comeca em "
                         f"{topo_eco[0]!r} — mesma contradicao, do lado barato")
        if base not in esc:
            fails.append(f"baseline_author.model {base!r} nao esta na escada {esc}")
        else:
            i = esc.index(base)
            esperado = {
                "executor": base,
                "passo_1": esc[max(0, i - 1)],
                "passo_2": esc[min(len(esc) - 1, i + 1)],
                "juncoes": esc[max(0, i - 1)],
                "mecanico": esc[0],
            }
            # [qa-critic Sonnet 19/08/2026, achado ALTA] na BORDA da escada o degrau que faltaria
            # nao existe, e a formula devolvia o PROPRIO modelo do autor para o 2o QA — critico igual
            # ao avaliado, com o canario dizendo que estava certo. O ADR declarava a regra de borda em
            # prosa; agora ela e' codigo.
            # [qa-critic Fable 19/08/2026, achado MEDIA-ALTA] a versao anterior desta checagem
            # EXIGIA que, na borda, o 2o QA fosse o MESMO modelo do autor — e reprovava quem
            # configurasse um modelo distinto, que e' justamente o que o ADR-018 quer. O gate
            # reprovava a configuracao honesta e aceitava a enviesada. Agora:
            #   - modelo DISTINTO do autor: sempre aceito, e' o preferido, nao precisa declarar nada;
            #   - modelo IGUAL ao autor: aceito so com declaracao SUBSTANTIVA (nao um "x").
            for papel in ("passo_1", "passo_2", "juncoes"):
                bloco = qfd.get(papel) or {}
                quem = bloco.get("resolve_hoje")
                ideal = esperado[papel]
                if quem == ideal:
                    continue                      # o degrau que a escada calcula: nada a discutir
                if quem in esc and quem != esperado["executor"]:
                    continue                      # outro degrau, mas distinto do autor: aceito
                declaracao = str(bloco.get("borda_declarada") or "").strip()
                if quem == esperado["executor"]:
                    if len(declaracao) < 40:
                        fails.append(f"qa_final_duplo.{papel}.resolve_hoje = {quem!r}, o MESMO modelo do "
                                     f"autor — e' o vies que o ADR-018 proibe. Ou use um degrau distinto, "
                                     f"ou escreva em `borda_declarada` por que a heterogeneidade esta "
                                     f"indisponivel (o texto atual tem {len(declaracao)} caracteres; "
                                     f"exige-se explicacao, nao carimbo)")
                else:
                    fails.append(f"qa_final_duplo.{papel}.resolve_hoje = {quem!r} nao esta na escada "
                                 f"{esc}")
            # [DECISAO DO DONO 19/08/2026] o degrau ACIMA do default (2o QA final) deixou de ser
            # automatico: rodar por reflexo esgotou a janela de 5h de tokens de uma sessao. Ele passa
            # a exigir AUTORIZACAO ATIVA - ordem direta do dono ou pergunta respondida com sim. Sem
            # esta assercao, afrouxar a regra de volta para automatico nao reprovaria nada, e o
            # afrouxamento silencioso e' exatamente a classe de regressao que este canario existe
            # para pegar. O texto e' exigido SUBSTANTIVO (nao um carimbo) pela mesma razao ja
            # aplicada a `borda_declarada` acima.
            p2 = qfd.get("passo_2") or {}
            autoriz = str(p2.get("autorizacao") or "").strip()
            if "ATIVA" not in autoriz.upper() or len(autoriz) < 80:
                fails.append(
                    "qa_final_duplo.passo_2.autorizacao ausente ou raso "
                    f"({len(autoriz)} caracteres) - a decisao do dono 19/08/2026 e' que o degrau "
                    "ACIMA do default NUNCA roda por default: so com ordem explicita ou pergunta "
                    "respondida. Exige-se o criterio escrito, nao um carimbo")
            # [2o QA Fable 20/08/2026] a checagem passou a ser do VALOR, nao da prosa: o
            # critico inverteu o sentido do texto mantendo as palavras-chave e a suite ficou
            # verde. Booleano nao se inverte mantendo as palavras.
            if p2.get("roda_sem_resposta") is not False:
                fails.append(
                    f"qa_final_duplo.passo_2.roda_sem_resposta = "
                    f"{p2.get('roda_sem_resposta')!r}; tem de ser exatamente False. E' o "
                    f"campo que decide se o degrau ACIMA dispara sem resposta do dono, e ele "
                    f"e' booleano de proposito: a versao anterior verificava PROSA por "
                    f"substring e o 2o QA inverteu o sentido mantendo as palavras-chave")
            sem_resp = str(p2.get("default_sem_resposta") or "").strip().upper()
            if "NAO RODA" not in sem_resp:
                fails.append(
                    f"qa_final_duplo.passo_2.default_sem_resposta = {p2.get('default_sem_resposta')!r}; "
                    "o default na AUSENCIA de resposta tem de ser NAO RODA. Qualquer outro default "
                    "devolve o automatismo pela porta dos fundos")
            if "autorizacao ativa" not in str(qfd.get("proibido") or "").lower():
                fails.append(
                    "qa_final_duplo.proibido nao lista o degrau acima rodando SEM autorizacao ativa - "
                    "a proibicao precisa estar onde quem le as proibicoes olha")
            for papel in ("executor", "mecanico"):
                bloco = qfd.get(papel) or {}
                if bloco.get("resolve_hoje") != esperado[papel]:
                    fails.append(f"qa_final_duplo.{papel}.resolve_hoje = "
                                 f"{bloco.get('resolve_hoje')!r}; a escada com default {base!r} "
                                 f"resolve para {esperado[papel]!r}")

    # [DECISAO DO DONO 19/08/2026] "nao teremos autor sonnet - autor sempre default". A checagem
    # abaixo cobria SO `developer`, e `author_roles` era lista decorativa: ninguem resolvia o conjunto.
    # Resolvendo todos, `docops-generative` apareceu em HAIKU (a regra `docops`/economy vem antes no
    # arquivo e o match e' por substring, entao engolia a especifica) - dois degraus ABAIXO do default,
    # o "PROIBIDO silencioso" que o proprio baseline_author descreve. Este laco e' o eval que faltava:
    # ele falha por PAPEL, dizendo qual, para o proximo bug do genero nao precisar ser adivinhado.
    if isinstance(ba, dict) and ba.get("model") in (esc or []):
        base_i = esc.index(ba["model"])
        for papel in (ba.get("author_roles") or []):
            fam_a, _w = handoff.suggest_model(papel, "low", ba["model"])
            if fam_a not in esc:
                fails.append(f"papel autoral {papel!r} resolve para {fam_a!r}, fora da escada {esc}")
            elif esc.index(fam_a) < base_i:
                fails.append(
                    f"papel autoral {papel!r} resolve para {fam_a!r}, ABAIXO do default "
                    f"{ba['model']!r} - viola a invariante 'autor sempre default' (dono, 19/08/2026) e o "
                    f"'PROIBIDO silencioso' do proprio baseline_author. Ordem das regras em `roles` "
                    f"importa: o match e' por SUBSTRING e o primeiro vence")
            elif esc.index(fam_a) > base_i:
                fails.append(
                    f"papel autoral {papel!r} resolve para {fam_a!r}, ACIMA do default {ba['model']!r} - "
                    f"o degrau acima nao roda por papel, so com autorizacao ativa "
                    f"(qa_final_duplo.passo_2.autorizacao)")
    # [ADR-110] o conserto da raiz vale se, e so se, a POSICAO da regra no arquivo nao importar.
    # Provamos permutando: a entrada mais especifica vai para o FIM e o papel autoral tem de
    # continuar no baseline. Antes do conserto isto resolvia para haiku. Este teste falha se alguem
    # voltar o casador para "primeiro do arquivo vence" — que e' a regressao real a temer, ja que a
    # regra `docops-generative` continuaria no lugar e o arquivo pareceria correto.
    if isinstance(ba, dict) and ba.get("model"):
        _salvo = handoff.POLICY["roles"]
        try:
            _perm = list(_salvo)
            _esp = [r for r in _perm if "docops-generative" in (r.get("match") or [])]
            if _esp:
                _perm.remove(_esp[0]); _perm.append(_esp[0])
                handoff.POLICY["roles"] = _perm
                _fam, _ = handoff.suggest_model("docops-generative", "low", ba["model"])
                if _fam != ba["model"]:
                    fails.append(
                        f"com a regra especifica no FIM do arquivo, 'docops-generative' resolve para "
                        f"{_fam!r} em vez do baseline {ba['model']!r} — o casador voltou a deixar a "
                        f"chave generica engolir a especifica, e a ordem do arquivo virou semantica "
                        f"de novo (ADR-110)")
        finally:
            handoff.POLICY["roles"] = _salvo

    if not str((ba or {}).get("author_invariant") or "").strip():
        fails.append("baseline_author.author_invariant ausente - a decisao do dono de que o autor e' "
                     "SEMPRE o default precisa estar escrita onde a politica vive")

    # [QA de juncao Sonnet 19/08/2026, achado ALTA] a versao anterior deste arquivo testava so
    # TOKENS CANONICOS ISOLADOS ("developer", "docops"), entao a suite ficava verde enquanto
    # `developer docops` resolvia para HAIKU — papel autoral dois degraus abaixo do default. A causa
    # era a ordem: a regra mecanica (economy) vinha ANTES da autoral (baseline), e chaves
    # independentes nao sao cobertas pela excecao de contencao. Agora o teste percorre o PRODUTO
    # CARTESIANO chave-autoral x chave-mecanica: exemplo que passa nao prova classe nenhuma.
    if isinstance(ba, dict) and ba.get("model") in (esc or []):
        _bi = esc.index(ba["model"])
        _aut, _mec = [], []
        for _r in (pol.get("roles") or []):
            if _r.get("tier") == "economy":
                _mec += _r.get("match") or []
            elif _r.get("tier") == "baseline":
                # [QA rodada 2, 19/08/2026, achado MEDIA-ALTA] a versao anterior filtrava por uma
                # lista ESCRITA A MAO ("developer","author","autor"), entao `architect` e `discovery`
                # — que tambem estao em author_roles — ficavam FORA do espaco testado. Reordenar a
                # regra `architect` para depois da mecanica reproduzia o mesmo bug sem nada apitar.
                # Lista a mao dentro de um teste envelhece igual a prosa que o teste deveria
                # substituir: o conjunto agora e' DERIVADO do proprio arquivo (todo tier baseline).
                _aut += _r.get("match") or []
        _quebras = []
        for _a in _aut:
            for _m in _mec:
                for _frase in (f"{_a} {_m}", f"{_m} {_a}"):
                    _f, _ = handoff.suggest_model(_frase, "low", ba["model"])
                    if _f in esc and esc.index(_f) < _bi:
                        _quebras.append((_frase, _f))
        if _quebras:
            _am = ", ".join(f"{f!r}->{v}" for f, v in _quebras[:4])
            fails.append(
                f"{len(_quebras)} papeis COMPOSTOS (gatilho autoral + gatilho mecanico) resolvem ABAIXO "
                f"do default {ba['model']!r}: {_am}. A ordem de `roles` E' a precedencia do casador — a "
                f"regra autoral tem de vir ANTES da mecanica (ADR-110)")
        elif len(_aut) * len(_mec) == 0:
            fails.append("produto cartesiano autoral x mecanico vazio — o teste nao esta exercitando "
                         "nada; confira os tiers em `roles`")

    # [2o QA Fable 19-20/08/2026, achado ALTA] o cartesiano acima cobria autoral x mecanica e
    # PAROU AI. A precedencia declarada e' SEGURANCA > autoral > mecanico, e o degrau de SEGURANCA
    # nao tinha teste: movendo a regra `qa/critic` para o fim de `roles`, a suite ficava VERDE
    # enquanto "qa do developer", "revisar a implementacao do developer" e "review do design"
    # resolviam para o modelo do PROPRIO AUTOR — exatamente o auto-vies que o ADR-018 proibe, e o
    # oposto do que docs/adr/110 afirma ("reprova qualquer configuracao que tire QA do degrau
    # heterogeneo"). Mesmo defeito da rodada anterior — espaco testado menor que o espaco
    # declarado — uma camada acima. Agora: papel COMPOSTO que contenha gatilho de QA tem de sair
    # heterogeneo, isto e', NUNCA no modelo do autor, venha o outro gatilho de onde vier.
    if isinstance(ba, dict) and ba.get("model"):
        _base = ba["model"]
        _qa_keys, _outras = [], []
        for _r in (pol.get("roles") or []):
            if _r.get("tier") == "heterogeneous":
                _qa_keys += _r.get("match") or []
            else:
                _outras += _r.get("match") or []
        _viol = []
        for _q in _qa_keys:
            for _o in _outras:
                for _frase in (f"{_q} do {_o}", f"{_o} {_q}"):
                    _f, _ = handoff.suggest_model(_frase, "low", _base)
                    if _f == _base:
                        _viol.append((_frase, _f))
        if _viol:
            _am = ", ".join(f"{f!r}->{v}" for f, v in _viol[:4])
            fails.append(
                f"{len(_viol)} papeis COMPOSTOS com gatilho de QA resolvem para o MODELO DO AUTOR "
                f"{_base!r}: {_am}. A regra `qa/critic` tem de vencer qualquer outra que case na mesma "
                f"frase — e' a precedencia de SEGURANCA (ADR-018 anti-vies), e ela vive na POSICAO da "
                f"regra em `roles`: ela e' a PRIMEIRA de proposito (ADR-110)")
        elif len(_qa_keys) * len(_outras) == 0:
            fails.append("cartesiano QA x demais vazio — o teste nao exercita nada; confira os tiers")

    fam_dev, _ = handoff.suggest_model("developer", "low", "opus")
    if fam_dev != (ba.get("model") if isinstance(ba, dict) else None):
        fails.append(f"developer (autoral) = {fam_dev}, esperado baseline {ba.get('model') if isinstance(ba, dict) else '?'}")

    # (b4) fallback de indisponibilidade (ADR-078: declarada via env, nunca sondada/silenciosa)
    saved_env = os.environ.get("FRAMEWORK_MODELS_UNAVAILABLE")
    try:
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable"
        # PORTADOR DO FALLBACK: `architect` saiu do tier max em 18/08 e `cross-ai` saiu em
        # 19/08. Depois disso NENHUM papel alcanca o tier `max` sozinho - so `risk_override`.
        # Entao quem exercita a degradacao da chain do max e 'developer com risco alto.
        # Se alguem devolver algum papel ao tier max, este teste continua valido: ele afirma a
        # degradacao, nao o portador.
        fam, why = handoff.suggest_model("developer", "high", "opus")
        if fam != "opus" or "fallback" not in why:
            fails.append(f"fable indisponivel: developer/high (risk_override -> max) = {fam} "
                         f"({why!r}), esperado opus com nota de fallback")
        fam, _ = handoff.suggest_model("cross-ai", "low", "opus")
        if fam != "opus":
            fails.append(f"cross-ai = {fam}, esperado baseline opus (saiu do tier max em 19/08)")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable,opus"
        fam, _ = handoff.suggest_model("discovery", "low", "opus")
        if fam != "sonnet":
            fails.append(f"fable+opus indisponiveis: discovery = {fam}, esperado sonnet")
        fam, _ = handoff.suggest_model("qa-critic", "low", "sonnet")
        if fam == "sonnet":
            fails.append("het com fable/opus indisponiveis devolveu o proprio autor sem esgotar haiku")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable,opus,haiku"
        fam, why = handoff.suggest_model("qa-critic", "low", "sonnet")
        if fam != "sonnet" or "DEGRAU 3" not in why:
            fails.append(f"het esgotado: = {fam} ({why!r}), esperado degrau 3 DECLARADO (mesmo modelo fresh)")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "fable,opus,sonnet"
        fam, why = handoff.suggest_model("developer", "low", "opus")
        if fam != "haiku" or "fallback" not in why:
            fails.append(f"balanced com sonnet/opus indisponiveis: = {fam} ({why!r}), "
                         f"esperado haiku com nota de fallback")
        os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = "haiku,sonnet"
        try:
            handoff.suggest_model("docops", "low", "opus")
            fails.append("chain economy esgotada deveria levantar erro declarado, nao escolher em silencio")
        except ValueError:
            pass
    finally:
        if saved_env is None:
            os.environ.pop("FRAMEWORK_MODELS_UNAVAILABLE", None)
        else:
            os.environ["FRAMEWORK_MODELS_UNAVAILABLE"] = saved_env

    # (c) determinismo RIGOROSO: congela TAMBEM o estado do repo e a rede (repo_state/pr_info
    # monkeypatch) -> prova que a CAMADA DE FORMATACAO e byte-identica dado o mesmo estado, nao so
    # ausencia de wall-clock (ressalva do qa-critic). Restaura os originais ao fim.
    orig_rs, orig_pr, orig_ea, orig_pa, orig_cf = (
        handoff.repo_state, handoff.pr_info, handoff.em_aberto,
        handoff.proposed_adrs, handoff.latest_checkpoint_field)
    try:
        FIXED = {"version": "9.9.9", "branch": "feat/x", "commit": "abc1234",
                 "origin": "git@example/repo", "unpushed": "?", "uncommitted": 0, "recent": ["a.py", "b.md"]}
        handoff.repo_state = lambda: dict(FIXED)
        handoff.pr_info = lambda branch: "(sem PR aberto para esta branch)"
        handoff.em_aberto = lambda: ["pendencia X"]
        handoff.proposed_adrs = lambda: []
        handoff.latest_checkpoint_field = lambda f: "Fazer Y (criterio: Z)"
        a = handoff.build("developer", "low", "opus", ts="2026-06-11T00:00:00Z")
        b = handoff.build("developer", "low", "opus", ts="2026-06-11T00:00:00Z")
        if a != b:
            fails.append("nao-deterministico: build() com MESMO estado deu saidas diferentes")
        # safety P14 (achado ALTO): unpushed='?' NUNCA pode render 'nada pendente'
        if "nada pendente" in a or "DESCONHECIDO" not in a:
            fails.append("unpushed='?' renderizou 'nada pendente' (falso) em vez de 'DESCONHECIDO' — P14 Acesso inseguro")
    finally:
        (handoff.repo_state, handoff.pr_info, handoff.em_aberto,
         handoff.proposed_adrs, handoff.latest_checkpoint_field) = (
            orig_rs, orig_pr, orig_ea, orig_pa, orig_cf)

    # --- ADR-095: modo PROCEDENCIA (carimbo em diretorio EXTERNO ao repo) -------------------
    import tempfile
    prov = handoff.provenance("/alvo/externo", ts="2026-07-22T00:00:00Z")
    # (a) campos DETERMINISTICOS do repo tem de aparecer
    for campo in ("metacognition-framework", "Versao", "Commit", "Operador humano"):
        if campo not in prov:
            fails.append(f"procedencia: campo deterministico ausente: {campo}")
    # (b) slots de dominio tem de ficar VISIVEIS (lacuna declarada, nao silencio)
    if "<preencher>" not in prov:
        fails.append("procedencia: nenhum SLOT '<preencher>' — lacuna de dominio ficaria silenciosa")
    # (c) status por artefato e o ponto todo do carimbo (minuta != registro)
    if "MINUTA" not in prov or "APROVADO" not in prov:
        fails.append("procedencia: taxonomia de status (MINUTA/PROPOSTA/MIGRADO/APROVADO) ausente")
    # (d) determinismo
    if prov != handoff.provenance("/alvo/externo", ts="2026-07-22T00:00:00Z"):
        fails.append("procedencia: nao-deterministico com mesmo estado/ts")
    # (e) RECUSA alvo dentro do repo (la a procedencia e o proprio git)
    if handoff.emit_provenance(os.path.join(handoff.ROOT, "tools"), "ts", write=False) != 2:
        fails.append("procedencia: aceitou alvo DENTRO do repo (devia recusar com exit 2)")
    # (f) recusa diretorio inexistente
    with tempfile.TemporaryDirectory() as td:
        if handoff.emit_provenance(os.path.join(td, "nao-existe"), "ts", write=False) != 2:
            fails.append("procedencia: aceitou diretorio inexistente (devia recusar com exit 2)")
        # (g) nao sobrescreve carimbo existente — apenda (traceability Regra 3)
        alvo = os.path.join(td, "externo")
        os.makedirs(alvo)
        handoff.emit_provenance(alvo, "2026-07-22T00:00:00Z", write=True)
        marca = "MARCA-QUE-NAO-PODE-SUMIR"
        with open(os.path.join(alvo, "PROCEDENCIA.md"), "a", encoding="utf-8") as fh:
            fh.write("\n" + marca + "\n")
        handoff.emit_provenance(alvo, "2026-07-23T00:00:00Z", write=True)
        txt = open(os.path.join(alvo, "PROCEDENCIA.md"), encoding="utf-8").read()
        if marca not in txt:
            fails.append("procedencia: SOBRESCREVEU carimbo existente (viola preservacao — Regra 3)")
        if "Sessao adicional" not in txt:
            fails.append("procedencia: 2a passagem nao apendou secao de sessao")

        # (h) NAO apenda em documento alheio: arquivo existente que nao e carimbo (pasta
        #     reaproveitada, arquivo vazio/truncado) — devia recusar, nao colar rabo sem cabeca.
        alheio_dir = os.path.join(td, "alheio")
        os.makedirs(alheio_dir)
        alheio = os.path.join(alheio_dir, "PROCEDENCIA.md")
        for conteudo in ("", "# Outro documento qualquer\n\ntexto de outra demanda\n"):
            with open(alheio, "w", encoding="utf-8") as fh:
                fh.write(conteudo)
            if handoff.emit_provenance(alheio_dir, "ts", write=True) != 2:
                fails.append("procedencia: apendou/sobrescreveu arquivo que NAO e carimbo "
                             f"(conteudo={conteudo!r:.30})")
            if open(alheio, encoding="utf-8").read() != conteudo:
                fails.append("procedencia: alterou documento alheio (devia deixar intacto)")

        # (i) --write COM caminho no modo procedencia: destino e sempre <DIR>/PROCEDENCIA.md.
        #     Aceitar e descartar em silencio e armadilha de CLI.
        limpo = os.path.join(td, "limpo")
        os.makedirs(limpo)
        if handoff.main(["handoff.py", "--provenance", limpo, "--write", "algum/caminho"]) != 2:
            fails.append("procedencia: --write com caminho foi aceito e descartado em silencio")

    # (j) guarda robusta a path exotico — commonpath levanta ValueError em drive diferente/UNC,
    #     que e JUSTAMENTE o caso de uso primario (drive corporativo sincronizado / share de rede).
    for exotico in ("D:\\NaoExisteDrive\\Chamado123", "\\\\servidor\\share\\Chamado123"):
        try:
            rc = handoff.emit_provenance(exotico, "ts", write=False)
        except Exception as e:  # noqa: BLE001 — qualquer excecao aqui e o bug
            fails.append(f"procedencia: guarda estourou {type(e).__name__} em alvo exotico {exotico}")
        else:
            if rc != 2:
                fails.append(f"procedencia: alvo exotico inexistente {exotico} devia dar exit 2, deu {rc}")

    # (k) bypass por CASE: filesystem Windows e case-INSENSITIVE, commonpath compara
    #     case-SENSITIVE — sem normcase, alvo DENTRO do repo passa como 'externo'.
    if os.name == "nt":
        if not handoff._inside_repo(os.path.join(handoff.ROOT.upper(), "tools")):
            fails.append("procedencia: guarda furada por CASE — alvo dentro do repo passou como externo")

    print(f"handoff: 6 campos P14; {len(MODEL_CASES)} regras de modelo; {len(ROLE_CASES)} inferencias; "
          f"deterministico; procedencia ADR-095 (11 checks) — {'OK' if not fails else 'FAIL'}")
    for f in fails:
        print("  -", f)
    print("-" * 50)
    print("RESULTADO:", "PASS (gerador roda, regra papel+risco correta, deterministico)" if not fails
          else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
