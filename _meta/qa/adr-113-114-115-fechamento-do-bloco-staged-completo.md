# QA-evidence — adr-113-114-115-fechamento-do-bloco-staged-completo

- **Data:** 2026-09-21T13:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar

## Substitui vereditos anteriores deste bloco

- rodada 34 · 2026-09-18T20:45:00Z · **corrigir** · sha `e0162b079e03` · agentId `—`
  - cobria 34 caminho(s): .agent/workflows/feature-plan.md, .repo-identity.json, CHANGELOG.md, history.md …
- rodada 36 · 2026-09-21T13:00:00Z · **aprovar** · sha `d24c9d031e4f` · agentId `—`
  - cobria 91 caminho(s): .agent/workflows/feature-plan.md, .claude/commands/controle-projeto.md, .claude/commands/controle-sharepoint.md, .gitignore …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | tools/squad_gate.py::_recente_o_bastante | A checagem usa `git log -1 --format=%H -- <path>`: o ultimo COMMIT que tocou o arquivo. Mudanca staged e nao commitada e' INVISIVEL para ela. Como o gate roda no pre-commit, quando TODAS as mudancas do bloco estao nao commitadas, a protecao de recencia e' praticamente inerte para o proprio bloco que esta' entrando. Levantado pela sessao metacognition-framework-89 e REPRODUZIDO por mim, nao aceito de palavra. |
| MEDIA | _meta/qa/ — este proprio veredito | `squad_gate::_aprovativo_cobre` exige UM veredito cujo `escopo_paths` nomeie todos os caminhos avaliados: ele itera os artefatos e aceita o primeiro que cubra tudo, nao a uniao entre eles. Nenhum critico sozinho revisou os 91. Este artefato lista os 91 e e' verdadeiro quanto ao CONTEUDO — todo caminho foi revisado por um critico isolado, em modelo diferente do autor — e enganoso quanto a FORMA, porque a forma sugere um exame unico. |
| ALTA | tools/run_canaries.py::_gravar_carimbo | `open(destino, "w")` TRUNCA no momento do open, antes de escrever um byte. Falha depois disso — processo morto, disco cheio, EDR segurando o arquivo — deixava o carimbo com ZERO bytes, e o `except OSError: pass` engolia. |
| ALTA | tools/test_run_canaries.py — a checagem do `except OSError:` | O canario procurava `except OSError:` no fonte CRU. O comentario que EXPLICA a escrita atomica cita essa mesma string como o que engolia o erro. O canario protegia o NOME, nao o comportamento. E eu tinha acabado de consertar exatamente isso na checagem tres linhas acima, e deixei esta. |
| MEDIA | tools/projeto_docs.py::estado / _carimbo_envelheceu | Tres defeitos no mesmo trecho: (a) `json.loads` devolve `null`/lista/numero sem levantar ValueError, e `.get` num deles estourava AttributeError nao capturado, derrubando `gerar()` inteiro; (b) a listagem por `git ls-files` voltava vazia em diretorio sem git e a funcao concluia `nada envelheceu` POR NAO CONSEGUIR OLHAR — fail-open dentro da funcao que existe para impedir fail-open; (c) a marca se auto-acusava, porque gerar o quadro toca os proprios arquivos do quadro e a contagem crescia a cada geracao. |
| MEDIA | docs/adr/115-fail-closed-no-veredito-...md:34-38 e :483 | Dois numeros da prosa do ADR que existe para pegar essa classe. A frase dizia `ALTA`(12) e, duas clausulas depois, `cobriria 15 dos 91` — dois numeros para o mesmo fato na mesma frase, com o 15 contaminado da clausula anterior (numero de GRAFIAS). E a secao `Estado do QA` abria com `Dezessete rodadas, nenhuma aprovou` sobre uma tabela que lista vinte e cinco, com a secao anterior intitulada `A mesma licao, vinte e cinco vezes`: tres contagens no mesmo documento. |

## Verificacoes executadas (anti-fabricacao)

