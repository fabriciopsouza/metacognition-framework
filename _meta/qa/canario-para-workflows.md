# QA-evidence — canario-para-workflows

- **Data:** 2026-09-23T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/test_skill_contract.py::classes_de_reversibilidade e autoteste_workflows | Entrada: acrescentar a palavra 'irreversivel' a definicao de E3 em `_shared/action-safety/SKILL.md`, como um autor faria de boa-fe ao explicar que uma publicacao nao se desfaz. Comportamento errado observado pelo critico, com exit 0: `reversiveis` vira {E1,E2,E3} e um workflow citando E3 como classe de reversibilidade — a mesma estrutura do bug real — passa limpo. Os dois guards existentes so' reagiam a conjunto VAZIO, nunca a conjunto ERRADO-MAS-NAO-VAZIO: a checagem nao desligava, ficava silenciosamente mais permissiva. CORRIGIDO sem voltar a cravar: a derivacao continua mandando no julgamento, e entrou um canario SOBRE a derivacao (`REVERSIBILIDADE_CANONICA`) que reprova alto se o conjunto mudar, pedindo que se atualize a constante E se diga por que. |
| MEDIA | tools/test_skill_contract.py::_RE_REVERSIVEL | Entrada: linha dizendo 'Este paragrafo NAO fala de reversibilidade, apenas cita E5 por outro motivo'. Observado: o regex casa 'reversibilidade' dentro da negacao, a linha e' tratada como se tratasse do assunto, e e' flagada por engano. CORRIGIDO com `_RE_NEGA_ASSUNTO`, que reconhece a negacao explicita do assunto, mais fixture de regressao. |
| MEDIA | tools/test_skill_contract.py - checagem de procedencia | Entrada: a frase exata do bug original ('o passo final corta o process-critic de J6') com um rodape descolado citando ADR-045 e ADR-011 sobre outro assunto. Observado: passa limpa, porque a checagem era substring no ARQUIVO INTEIRO. Ganhavel mesmo sem ma-fe. CORRIGIDO com uma segunda checagem POR LINHA: a linha que junta siglas de ADRs diferentes tem de citar as duas NELA. O piso por arquivo fica, porque teria pego os dois bugs reais tal como ocorreram — nenhum dos dois citava ADR nenhuma. |
| MEDIA | tools/test_skill_contract.py::_RE_SIGLA | Entrada: 'Process-Critic de j6' — variacao natural de maiuscula no inicio de frase, nao ofuscacao. Observado: escapava das DUAS checagens, porque o regex usava J[0-6] maiusculo fixo e o literal minusculo. CORRIGIDO com re.I e normalizacao para maiuscula na consulta ao mapa, mais fixture. |
| BAIXA | tools/test_skill_contract.py - uniao redundante em conferir_workflows | O conjunto `{s for s in ('process-critic',) if s in texto}` nunca mudava o resultado, porque `_RE_SIGLA` ja' inclui o literal na alternacao. Codigo morto num canario e' confusao futura. REMOVIDO. |
| BAIXA | tools/test_skill_contract.py::autoteste_workflows - cobertura de regressao | Faltavam fixtures para o conjunto de reversibilidade contaminado e para sigla citada com o ADR ERRADO. A logica cobria o segundo caso, mas sem fixture que provasse que continua verdade apos refactor. CORRIGIDO: o autoteste subiu de 3 para 7 casos, e o rotulo do numero passou a ser CONTADO da fonte em vez de digitado — a 1a versao dizia '3 fixtures' sobre um corpo de 7, que e' a mesma classe de defeito que este bloco persegue. |
| BAIXA | .agent/workflows/feature-plan.md - a linha que distingue J6 do process-critic | O canario novo reprovou o ARQUIVO REAL: a linha que faz a distincao citava so' o ADR-045, e o ADR-011 estava duas linhas abaixo. Achado verdadeiro contra o texto do proprio autor. CORRIGIDO no documento, nao na regra — quem faz a distincao deve mostrar as duas fontes ali. |

## Verificacoes executadas (anti-fabricacao)

- critico rodou `python tools/test_skill_contract.py` no repo real: PASS, 13 skills, 7 workflows, 0 problemas
- critico PROVOU o ALTA com experimento reproduzivel: copiou action-safety para um scratch, acrescentou uma frase plausivel a definicao de E3, e o canario aceitou um workflow citando E3 como classe de reversibilidade com RESULTADO PASS e EXIT 0 — sem nenhum sinal em conferir_workflows nem em autoteste_workflows
- critico reproduziu tambem o caso VAZIO (fonte reformatada em tabela) e confirmou que ESSE o canario pega — provando que o buraco era so' o caso parcial
- critico provou o falso-positivo da negacao: linha dizendo 'NAO fala de reversibilidade' citando E5 era flagada por engano
- critico provou que a procedencia era ganhavel: a frase exata do bug original passa limpa se as duas ADRs aparecerem num rodape sem relacao, porque a checagem era substring no arquivo inteiro
- critico provou o bypass por maiuscula: 'Process-Critic de j6' escapava das duas checagens, porque `_RE_SIGLA` nao tinha re.I
- critico confirmou por teste que a regra 'basta 1 classe certa citada para nao reprovar' NAO e' bug — e' necessaria, senao `feature-plan.md:16` quebraria
- critico confirmou a integracao com run_canaries.py por leitura do discover() e por execucao direta de main() com um workflow ruim: EXIT 1
- autor provou o canario no arquivo REAL, nao so' em fixture: copiou `.agent/workflows/feature-plan.md`, desfez as duas correcoes de 21/09, e o canario detectou AS DUAS; com o arquivo intacto, zero falso-positivo
- autor, APOS as correcoes: test_skill_contract.py PASS com 7 fixtures de workflow; suite completa 88 PASS / 1 SKIP / 0 FAIL, exit 0
- autor reaplicou a mao os dois gates que o hook declarava inertes: sync em dia e check_core_agnostic PASS
