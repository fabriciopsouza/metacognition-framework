# B1 — Análise acompanhada: especificação de execução

- Origem: plano aprovado pelo dono em 19/11/2026, repositório central de pesquisas, `2026-11-19_analise-acompanhada-humano-ia/relatorio.md`, seções 7.0 a 7.8 (bloco B1).
- Faixa: F2 (regra do framework e ADR). Autor: Opus. Revisão da especificação, rodada 1: Codex chamado (id 20261119-223512-c1f3b0), sem leitura de arquivos por política do ambiente dele (veredito não técnico; 3 notas aproveitadas); Sonnet 5.5 assumiu como fallback declarado: APROVADO COM RESSALVAS, 6 achados, todos aplicados. Revisão do conjunto: Codex (família oposta à última rodada).
- Branch: `feat/b1-analise-acompanhada` (worktree própria, a partir de `origin/main` 2e658c4).

## 1. Entregas

| # | Entrega | Arquivo | Nova/alterada |
|---|---|---|---|
| E1 | ADR-134 "Análise acompanhada humano-IA" (Aceito): modos, regras de sessão, classes de decisão, painel mínimo, invariante por operação, relação com ADR-089 e ADR-122, apêndice A fora | `docs/adr/134-analise-acompanhada.md` | nova |
| E2 | Skill condutora `analise-dados`: gatilho, modos (7.4), ciclo por fase (7.6), painel mínimo, catálogo (7.5), classes de decisão (7.7), diário e D-nn, entregas mínimas por fase, delegação com "modo" | `.agent/skills/analise-dados/SKILL.md` | nova |
| E3 | Sub-modo `produto-de-dados` do discovery: filtro de entrada, banco 5.1, procedimento 5.2, saída; + 1 linha na tabela de sub-modos | `.agent/skills/discovery/produto-de-dados.md`; `.agent/skills/discovery/SKILL.md` | nova; alterada |
| E4 | Emenda do ADR-089: ficha de insumo de 6 para 8 campos (7 **Alvo e métrica de sucesso**; 8 **Premissas editáveis**) e gatilho ampliado para o início da fase 1+2 de análise | `docs/adr/089-...md` (seção "Emenda 1"); discovery passo 4.1 | alterada |
| E5 | Canário da ficha com 8 campos | `tools/test_elicitation_gate.py` | alterada |
| E6 | Regra de uma linha na fonte global (seção 6 "Plano e comandos de sessão") | `.claude/global/CLAUDE-global.md` | alterada |
| E7 | Campo "modo" no pacote de handoff: `--modo acompanhado|autonomo` (padrão `acompanhado`) e `--modo-origem "<literal e hora da ordem>"`; seção `## [modo] análise de dados (ADR-134)` sempre emitida; `build(..., modo="acompanhado", modo_origem="")` mantém compatibilidade; `--modo autonomo` exige `--modo-origem` (sem ele, exit 2); acompanhado sem origem sai como "padrão da sessão" | `tools/handoff.py`; `tools/test_handoff.py` | alterada |
| E8 | Canário novo da fiação da análise acompanhada: skill existe com gatilho (dado, indicador, métrica, modelo) e exclusão; regra global aponta a skill e o padrão acompanhado; linha do sub-modo na tabela e companion existe; skill cita as 7 classes de decisão e os 7 itens do painel. Autoteste com fixture sabotada | `tools/test_analise_dados.py` | nova (acréscimo ao plano: sem ele a regra global e a skill seriam só prosa — regra "capacidade determinística onde há ganho") |
| E9 | Registro: CHANGELOG (ADR-134 + emenda ADR-089), `capabilities.json` (+`analise-acompanhada`; título de `elicitation-gate` 6→8 campos), `CAPABILITIES.md` regerado | raiz | alterada |
| E10 | Depois do merge: `python bootstrap.py` no clone canônico (espelha a skill em `~/.claude/skills` e renderiza a regra no CLAUDE.md global) e teste de ativação 3/3 com sinal, 0/3 sem | fora do diff | operação |

## 2. Decisões do autor (premissas declaradas)

1. Número do ADR: 134 (133 é o último no `main`; 130 está em PRs abertos).
2. A skill não inclui ferramenta de invariante: isso é o B2. Até lá, a skill manda declarar a invariante e conferi-la com o script do projeto.
3. Pacote web: a skill entra no tier premium como papel lateral (`LATERAL` de `tools/web_export.py`) e o README gerado passa a calcular a contagem (16). Decisão revista depois da revisão do conjunto (Codex, achado 5): incluir custava duas linhas, e adiar era desvio do plano.
4. Nenhum nome de empresa, tabela, sigla ou valor de projeto entra (isolamento, regra 9). Exemplos neutros.
5. A regra global fica na seção 6 porque trata de modo de sessão.
6. A ficha continua disparando só em risco alto para escrever código (texto atual); o acréscimo é o disparo no início da fase 1+2 da skill `analise-dados`, qualquer risco, com autopreenchimento declarado quando há fonte inequívoca.

## 3. Aceite

1. Todos os canários listados no plano passam: `test_elicitation_gate`, `test_handoff`, `test_rules_parity`, `test_elicitation_catalog`, `test_adr_changelog_sync`, `test_skill_contract`, `validate_skills`, `test_capabilities`, `test_web_export`, `test_discovery_eval`, `test_core_no_vendor`; mais o novo `test_analise_dados`; e a bateria `tools/run_canaries.py` sem falha nova em relação à linha de base.
2. Sabotagens (em cópia, uma por invariante):
   - S1a: retirar "Alvo e métrica de sucesso" da ficha → `test_elicitation_gate` reprova.
   - S1b: retirar "Premissas editáveis" da ficha → `test_elicitation_gate` reprova.
   - S1c: retirar o parágrafo "Disparo ampliado" do passo 4.1 → `test_elicitation_gate` reprova.
   - S2a: pacote de handoff sem a seção "modo" → `test_handoff` reprova.
   - S2b: `--modo autonomo` sem `--modo-origem` aceito (exit 0) → `test_handoff` reprova (a ordem de autônomo precisa do literal e da hora, regra 7.4 "onde o modo mora").
   - S3a: regra global sem `analise-dados` → `test_analise_dados` reprova.
   - S3b: skill sem uma das 7 classes de decisão ou sem um dos 7 itens do painel → `test_analise_dados` reprova.
   - S3c: tabela de sub-modos sem a linha `produto-de-dados.md` → `test_analise_dados` reprova.
3. Teste de ativação (E10): 3/3 e 0/3. Teste de comportamento do modelo, não determinístico; débito de prova por prosa, repetido no piloto B4. Protocolo: 6 sessões novas sem histórico (`claude -p` com saída `stream-json`) numa **pasta neutra vazia** (fora de qualquer repositório, para valer só o que o bootstrap instala em `~/.claude`), depois do `python bootstrap.py` no clone canônico (grava em `~/.claude`, fora do diff); ativação = chamada da ferramenta Skill com `analise-dados` no fluxo. Com sinal: (1) "confira se a soma de vendas por mês em vendas.csv bate com o total de 1.250" (CSV pequeno criado na pasta neutra); (2) "quero prever a demanda das próximas 4 semanas"; (3) "defina a regra do indicador de atraso de entrega". Sem sinal: (4) "corrija o erro de digitação no README"; (5) "renomeie a função foo para bar"; (6) "escreva um e-mail de agradecimento à equipe". Evidência: saída de cada sessão anexada ao veredito.

## 4. Fora

B2 (ferramenta de invariante, QA de análise), B3 (modelo de runbook), B4–B5, apêndice A (orquestrador, painel, AGENTS.md/GEMINI.md).
