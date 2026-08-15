# QA-evidence — pr-118-recencia-do-veredito-no-squad-gate

- **Data:** 2026-08-14T14:39:09Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** leitura do historico das 8 rodadas anteriores, do diff completo e do ci.yml antes de afirmar qualquer coisa sobre o fluxo real
- **RRC:** PASSA — o critico revisou em worktree isolado no commit exato, rodou a suite, o pytest e o gate por conta propria, e reproduziu ao vivo tanto o caso que aprova quanto a ressalva que levanta, em vez de aceitar a mensagem do commit.
- **Metodo-senior:** N/A: revisao adversarial de PROCESSO sobre bloco alheio, sem autoria de norma/spec/ADR nova pelo critico.

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| medio | tools/run_canaries.py:69-86 (_contar dentro de _contar_testes_e_entrypoint) | A contagem desce em if/try/with mas nao em for/while/match. Uma funcao `test_*` definida no nivel de modulo dentro de um `for` vira nome em globals() e E' coletada pelo pytest, mas a contagem devolve 0 — entao o guard de canario cego nao dispara e o runner reporta PASS sem executar assercao. E' a mesma classe que o guard existe para impedir. |
| baixo | tools/squad_gate.py:144-159 (_recente_o_bastante) | Nao e' defeito, e' assimetria documentada: no fluxo local (git diff --cached) um arquivo novo apenas staged e' bloqueado; no CI, ja commitado, passa. O comportamento local e' mais estrito por desenho, e o comentario do codigo declara a intencao. |

## Verificacoes executadas (anti-fabricacao)

- git worktree add --detach em 6792400 -> revisao isolada do trabalho em curso na arvore principal
- python tools/run_canaries.py no worktree -> 66 PASS / 1 SKIP / 0 FAIL; nenhum FAIL(cego)
- python tools/test_squad_gate.py -> 26 PASS / 0 FAIL; python -m pytest -> 26 passed (paridade confirmada)
- Arquivo novo COMMITADO + diff estilo CI (git diff --name-only BASE HEAD) -> ja tem historico -> squad_gate responde OK: o fix NAO cria falso positivo no fluxo de CI
- Arquivo novo apenas STAGED + veredito de escopo amplo -> BLOQUEADO (exit 1): confirma o fail-closed pretendido no fluxo local
- Canario sintetico com `def test_*` dentro de `for` de modulo e `assert False` -> reportado PASS sem executar a assercao (ressalva media reproduzida ao vivo)
- Mesmo caso com `while` e `match` -> (0, False): o gap nao e' exclusivo do `for`
- Varredura AST em todos os tools/test_*.py -> nenhum define test_* dentro de for/while: gap LATENTE, nao ativo
- Sanidade da contagem: closure dentro de funcao -> nao conta (correto, pytest nao coleta); classe 'TestesDoGate' -> conta (prefixo Test); 'GateTests' -> nao conta (alinhado ao default do pytest); try/except/else/finally -> os 4 ramos contados
- Leitura linha a linha dos 3 testes repontados: confirmado que ANTES desta correcao eles passavam EXPLORANDO o bug do `continue` (path ficticio sem historico escapava da ancestralidade); agora usam paths reais com historico verificado
- grep sha_revisado em qa_evidence.py -> carimbado no momento da gravacao; a divida declarada no commit continua real e nao foi silenciosamente resolvida nem sobre-alegada
- git worktree remove --force; git status identico ao snapshot inicial, sem residuo de sabotagem
- RECARIMBO (2026-08-15, nao pelo critico): o rebase sobre origin/main orfanou 6792400 — `git merge-base --is-ancestor 6792400 HEAD` -> falso, nenhuma branch o contem. O sobrevivente e' 742745c, e `git patch-id --stable` devolve 5c72015a1396aab0efaaf359ec750771d3afe7b1 para OS DOIS: a mudanca revisada e' identica. RESSALVA: as ARVORES nao sao identicas — a de 742745c tem a mais `docs/_private/reports/emendas-ao-prompt-de-retomada-2026-08-14.md` (+192 linhas, doc-only, entrou pelo PR #119), arquivo que o critico NAO viu. Nenhum path de `escopo_paths` difere.
