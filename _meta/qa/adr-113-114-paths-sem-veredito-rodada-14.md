# QA-evidence — adr-113-114-paths-sem-veredito-rodada-14

- **Data:** 2026-09-12T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Postura (posture-gate — atestada pelo qa-critic adversarial)
- **Discovery:** —
- **RRC:** —
- **Metodo-senior:** —

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | _shared/controle-projeto/SKILL.md:123 e docs/adr/113-politica-de-lancamento-de-projeto-como-pacote-resolvido.md:103 | citacao morta: 'git show --stat f6a334d' apresentado como prova conferivel em dois documentos canonicos, sendo que o hash nao existe neste repositorio e nenhum dos dois dizia onde existiria. Quem tentasse conferir recebia 'fatal', nao prova. Corrigido nomeando o repositorio (migracao-sac), citando a saida real conferida (8 files changed, 207 insertions, 490 deletions) e DECLARANDO o limite que o autor descobriu ao verificar: aquele repositorio e' local e sem remoto, entao o numero e' auditavel nesta maquina e nao por terceiro — [INFERIDO] verificado, nao fonte publica. |
| MEDIA | .claude/commands/controle-sharepoint.md:32-36 contra tools/controle_sharepoint.py:349 | o comando mandava relatar 'as tres listas que o ensaio produz' quando o codigo produz quatro: mudancas, ignorados, desconhecidos E recusados. A categoria omitida e' a que carrega a tese do modulo. Cenario real: 2 prazos recusados por formato nao entram no estado, o comando nao manda relatar, e o dono sai achando que o prazo mudou. Corrigido para quatro bullets, com o motivo escrito. |
| BAIXA | docs/_private/_intake/censo-vm-2026-08-20.json | expoe hostname (9TRP7H4), fabricante e modelo da maquina. Risco baixo e aceito: repo PRIVATE, docs/_private/ removido de todo export, nenhum dado de cliente ou credencial. O autor ja o havia movido da RAIZ para docs/_private/_intake/ nesta mesma sessao, antes da revisao. |

## Verificacoes executadas (anti-fabricacao)

- critico rodou run_canaries.py completo: 86 PASS, 1 SKIP (test_parity.py), 0 FAIL de 87
- critico rodou check_core_agnostic.py: PASS, 58 arquivos varridos, incluindo as 2 skills novas
- critico rodou test_marketing_claims.py: PASS, sem trecho alegando caso sem apontar fonte
- critico rodou test_controle_base/projeto/sharepoint: 164/141/68 verificacoes, batendo com a prosa
- critico rodou test_mutacao_controle.py: 34/34 mutacoes detectadas, batendo com '34 defeitos por mutacao'
- critico contou 'sabotagem detectada' em runtime: 11, batendo com '11 por sabotagem'
- critico rodou `git cat-file -t f6a334d` neste repo: 'fatal: Not a valid object name' — a citacao esta morta aqui
- critico leu export-clean.py e confirmou STRIP_BEFORE = ['docs/_private', '.git'], e que publish-clean.yml so publica por ele
- autor, apos os achados: localizou o commit f6a334d no repo migracao-sac e conferiu '8 files changed, 207 insertions(+), 490 deletions(-)' — os numeros da prosa estao CORRETOS, o defeito era a citacao sem endereco
- autor: descobriu que migracao-sac NAO tem remoto ('git remote get-url origin' -> erro), agravante que o critico nao tinha como ver; registrado na correcao
- autor, apos as correcoes: check_core_agnostic PASS e run_canaries 86 PASS, 1 SKIP, 0 FAIL
