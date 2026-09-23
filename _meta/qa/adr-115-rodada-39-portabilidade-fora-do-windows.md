# QA-evidence — adr-115-rodada-39-portabilidade-fora-do-windows

- **Data:** 2026-09-22T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Substitui vereditos anteriores deste bloco

- rodada 39 · 2026-09-22T00:00:00Z · **aprovar_com_ressalvas** · sha `f1d184c6edf9` · agentId `af2d8215b2fa52ac0`
  - cobria 4 caminho(s): tools/squad_gate.py, tools/test_controle_base.py, _meta/qa/adr-115-rodada-39-portabilidade-fora-do-windows.json, _meta/qa/adr-115-rodada-39-portabilidade-fora-do-windows.md

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/squad_gate.py::sha_do_veredito e os 20 pinos de VEREDITOS_LEGADOS | Entrada: rodar o canario dos vereditos legados em macOS ou Linux. Comportamento errado observado na CI: os 20 pinos acusavam 'alterados desde o congelamento' — porque foram calculados no Windows a partir dos bytes CRLF do checkout, enquanto o repositorio guarda LF. Um mecanismo de INTEGRIDADE que so' pode passar numa plataforma nao esta' medindo a evidencia, esta' medindo o sistema de arquivos. CORRIGIDO: o hash normaliza CRLF->LF antes de medir, e os 20 pinos foram recalculados para o hash de conteudo por script que ABORTA se algum arquivo divergir do pino ANTIGO pelos bytes crus — prova de que so' a funcao mudou, nao o conteudo. O critico refez essa verificacao por conta propria e confirmou nos 20. |
| ALTA | tools/test_controle_base.py - o caso 'somente-leitura -> mensagem, nao traceback' | Entrada: rodar o canario em POSIX. Dois comportamentos errados: (a) o teste tornava o ARQUIVO somente-leitura, mas `escrever_texto` grava um temporario ao lado e troca com os.replace, e no POSIX isso depende da permissao do DIRETORIO — a gravacao SUCEDIA e o teste reprovava uma garantia que de fato existe; (b) `stat.S_IWRITE` e' 0o200, write-only sem leitura, entao a restauracao tirava a permissao de LER e o `read_text` da checagem seguinte estourava PermissionError de verdade. CORRIGIDO: barreira por plataforma (diretorio 0o500 no POSIX, atributo do arquivo no Windows) e restauracao com 0o700/0o644. O codigo de producao nao foi tocado porque ja' estava certo. |
| MEDIA | tools/test_controle_base.py - a barreira POSIX sob UID 0 | Entrada: rodar o canario como root (o caso comum quando se troca `runs-on` por um job containerizado). Comportamento: o kernel POSIX ignora a permissao do diretorio para o UID 0, entao `chmod(pasta, 0o500)` nao barra nada, a gravacao sucede, e o caso volta a reprovar uma garantia que existe — agora tambem no Linux, que e' pior que o defeito original porque ninguem esperaria por ele ali. Hoje nao se materializa (CI em runner nao-root, verificado no ci.yml). CORRIGIDO declarando em vez de supondo: sob root o caso se ANUNCIA como nao-exercitado, em vez de carimbar um PASS que nao exercitou nada. |
| BAIXA | _meta/qa/release-1.89.0-passivo-do-registro-acabou.json | O blob commitado ja' contem sequencias \r\r\n (CR duplo antes do LF) dentro de um campo aninhado. E' PRE-EXISTENTE — `git diff --stat HEAD -- _meta/qa/` esta' vazio — e provavelmente veio de uma normalizacao malfeita anterior, ao colar transcript com CRLF num caminho que so' entende LF. NAO ha' risco de bypass: o critico verificou que todo \n do arquivo ja' tem \r antes, entao o autocrlf e' no-op nele em qualquer plataforma e o hash normalizado bate igual. Fica ABERTO como higiene de dado, para ser limpo se o veredito for reaberto algum dia. |

## Verificacoes executadas (anti-fabricacao)

- critico verificou de forma INDEPENDENTE, com script proprio e sem usar o do autor, que os 20 vereditos legados tem conteudo identico ao do HEAD apos normalizar fim de linha — nos 20
- critico confirmou que `git diff --stat HEAD -- _meta/qa/` esta vazio: nenhum dos 20 arquivos foi tocado neste bloco
- critico simulou o algoritmo REAL do autocrlf do git (insere \r so' antes de \n que ainda nao tem \r) e comparou checkout POSIX contra checkout Windows nos 20 arquivos: hash normalizado identico, zero divergencias
- critico DESCARTOU a propria simulacao ingenua inicial (converter todo \n em \r\n cegamente), que acusou falso-positivo em 1 arquivo — investigou e concluiu que o defeito era da simulacao dele, nao do conserto
- critico grepou todos os chamadores de sha_do_veredito: sao 2, ambos internos ao squad_gate, ambos consistentes com a normalizacao
- critico provou por MUTACAO REAL no Windows (nao por leitura): copiou controle_base.py e o canario para o scratchpad, trocou `except OSError` por `except ZeroDivisionError` DENTRO de escrever_texto, e o teste ficou vermelho com exit 1 — a assercao discrimina de verdade
- critico leu .github/workflows/ci.yml e confirmou que os jobs rodam direto nos runners, sem `container:`, logo nao-root — o que torna a ressalva do root dormente hoje
- critico rodou test_squad_gate.py (96 PASS / 0 FAIL), test_controle_base.py (PASS) e test_numeros_controle.py (PASS)
- autor, APOS fechar a ressalva do root: test_controle_base.py PASS, test_mutacao_controle.py PASS (34 mutacoes detectadas), test_numeros_controle.py PASS
- autor rodou a suite completa antes destes ultimos ajustes: 88 PASS / 1 SKIP / 0 FAIL, exit 0 — o critico NAO reconferiu este numero especifico, e isso esta' declarado em nao_verificado
