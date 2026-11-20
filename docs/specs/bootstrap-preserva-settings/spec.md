# Especificação — `bootstrap.py` preserva o `settings.json` versionado

- **Data:** 20/11/2026 · **Faixa:** F2 (gatilhos `permissao_credencial`, `multi_sessao_sistema_pessoa`) · **Decisão do dono:** opção (c), 20/11/2026.
- **Pendência de origem:** `trabalhos.py`, slug `bootstrap-preserva-settings`.

## 1. Problema

`python bootstrap.py` chama `activate_nonadmin()`, que copia `.claude/settings.nonadmin.json` por cima de `.claude/settings.json` do projeto. Esse arquivo é versionado e compartilhado por várias sessões. Resultado: os 6 tipos de hook somem, a árvore fica suja e um commit descuidado leva o desligamento dos gates para o `main`. Reincidiu em 09/10 e 20/11/2026.

## 2. Decisão (opção c)

O perfil non-admin passa a ser gravado em `.claude/settings.local.json` (já no `.gitignore`, linha 46), como `"disableAllHooks": true`.

**Prova de mecanismo (20/11/2026, executada):** pasta temporária com hook `UserPromptSubmit` no `settings.json` que grava um marcador. `claude -p` sem `settings.local.json`: marcador criado. Com `settings.local.json` = `{"disableAllHooks": true}`: marcador não criado. Copiar o conteúdo de `settings.nonadmin.json` para o local **não** funcionaria: hooks de arquivos diferentes se somam; o perfil sem hooks não remove os do projeto.

### 2a. Prova refeita (20/11/2026, Claude Code 2.1.326, `claude -p "responda apenas ok" --max-turns 1`)

| Passo | `settings.local.json` | Retorno | Hook rodou (marcador) |
|---|---|---|---|
| 1 | ausente | 0 | sim |
| 2 | `{"permissions":…, "disableAllHooks": true}` | 0 | **não** |
| 3 | `{"permissions":…}` (override removido) | 0 | sim |

## 3. Comportamento novo

| # | Situação | Resultado |
|---|---|---|
| C1 | `settings.local.json` ausente | cria `{"disableAllHooks": true}` |
| C2 | existe, JSON objeto válido, sem a chave | acrescenta a chave; demais chaves preservadas (ex.: `permissions`) |
| C3 | já tem `disableAllHooks: true` | não escreve; mensagem "já ativo" |
| C4 | JSON inválido ou não-objeto | recusa (retorno falso), não escreve, diz como corrigir |
| C5 | sempre | `.claude/settings.json` byte a byte igual ao de antes; nenhum `.bak` criado |

- Escrita atômica (arquivo temporário + `os.replace`), UTF-8, indentação 2.
- `activate_nonadmin(raiz=ROOT)` recebe a raiz por parâmetro, para o teste rodar em pasta temporária.
- `--check` (`verificar`): perfil = non-admin se o local tem `disableAllHooks: true` ou o `settings.json` não tem hooks; senão admin. Mensagem de reparo deixa de citar `settings.json.bak`.
- Volta ao modo com hooks: apagar a chave `disableAllHooks` do `settings.local.json` (mensagem final e guia dizem isso).

## 4. Fora do escopo

- Pacote público non-admin (`tools/export-clean.py`): continua usando `settings.nonadmin.json` como o `settings.json` do pacote. Sem mudança.
- Instalação antiga cujo `settings.json` já foi sobrescrito: não é migrada automaticamente; o guia diz como restaurar (`git checkout -- .claude/settings.json` feito pelo dono, ou `.bak`).
- Opção `--admin` para desfazer: não pedida.

## 4a. Revisão r1 da especificação (Codex `gpt-6.1-sol`, id `20261120-141529-dab648`, REPROVADO, 13 achados) — o que mudou

| Achado | Tratamento |
|---|---|
| A1 ALTA: o arquivo local vale para TODAS as sessões do clone; no clone canônico, `python bootstrap.py` pós-merge desligaria os hooks de todas, sem aparecer no `git status` | **Trava (b) somada à (c):** o override só é gravado quando o PowerShell **não** executa arquivo `.ps1` do jeito que os hooks executam. Onde executa (este PC), o bootstrap não toca em nenhum arquivo de configuração e diz isso. Forçar o perfil numa máquina com PowerShell = editar o local à mão (guia, opção C). |
| A1 (detecção) | `ps_available()` testava `-Command "exit 0"`, que a política de execução não bloqueia. Passa a rodar um `.ps1` temporário com `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`, o mesmo formato dos hooks. |
| A2 corrida com outra sessão | releitura dos bytes logo antes do `os.replace`; mudou → recusa sem escrever. Trava de arquivo: fora (janela de milissegundos; custo desproporcional). |
| A3/A8 `--check` | diz o que inspecionou: "override local `disableAllHooks`: ativo/inativo" e "hooks no settings.json do projeto: sim/não"; local inválido = BLOQUEIA com reparo; não afirma estado efetivo de hooks de usuário/plugin. |
| A4 falhas de arquivo | destino diretório, link, sem permissão, falha do temporário: retorno falso, mensagem acionável, original intacto, temporário apagado, sem mensagem de sucesso. Temporário no mesmo diretório. |
| A5 links | `settings.local.json` link simbólico/junção ou não-arquivo-regular → recusa. |
| A6 tipos | só `True` (booleano estrito, `is True`) conta como ativo; `False` ou ausente → grava `true`; qualquer outro tipo → recusa. |
| A7 BOM/comentário | leitura `utf-8-sig`, escrita UTF-8 sem BOM; comentário ou vírgula final = JSON inválido → recusa, arquivo intacto. |
| A9 prova | refeita com versão, controle positivo após remover o override (seção 2a). Sessão já aberta: efeito não garantido (DESCONHECIDO) — guia diz "vale a partir da próxima sessão". |
| A10/A12 textos | "remover o override local" (não "voltar ao admin"); recuperação de instalação antiga: conferir o diff antes, salvar a versão atual. |
| A11 aceite | comparação de bytes do `settings.json` e de `.bak` preexistente; repetição idempotente; testes de erro e do `--check`. |
| A13 | inventário de referências (`.bak`, cópia por cima) feito; `trabalhos.py` atualizado no fechamento. Alternativa por sessão (`claude --settings`) rejeitada: o usuário non-admin abre pela extensão do editor, não pela linha de comando. |

## 4b. Revisão r1 do conjunto (Codex `gpt-6.1-sol`, id `20261120-170948-a789b1`, REPROVADO, 4 achados) — tratamento

| Achado | Tratamento |
|---|---|
| 1 ALTA `ps_available()` aceitava `pwsh` | só `powershell.exe` (o que os hooks chamam); teste A1 com `which`/`run` simulados; sabotagem S7 |
| 2 MÉDIA texto não codificável escapava do tratamento | `except (OSError, UnicodeError)`; teste A4; sabotagem S8 |
| 3 MÉDIA testes não cobriam detecção, `--check`, falha de troca, link | `diagnostico_perfil()` extraída do `verificar()` e testada; testes A1, A4 (troca), A5 (link simulado) |
| 4 MÉDIA "hooks mantidos" com override ativo | com PowerShell, o bootstrap lê o local e avisa "override continua ATIVO"; teste e sabotagem S9 |

Prova após o tratamento: `tools/test_nonadmin.py` 22 de 22; 10 de 10 sabotagens pegas.

## 4c. Revisão r2 do conjunto (Sonnet 5.5, `qa-critic`, APROVADO COM RESSALVAS, 0 ALTA) — tratamento

| Achado | Tratamento |
|---|---|
| 1 MÉDIA teste deixava `__pycache__` na raiz | `sys.dont_write_bytecode` no import por caminho |
| 2 MÉDIA timeout da sonda = falso NÃO grava override no clone inteiro | `sondar_powershell()` devolve sim/barrado/ausente/indeterminado; timeout repete com 60 s; indeterminado não grava e sai com 1; testes e sabotagens S11, S12 |
| 3 BAIXA `mkstemp` fora do `try` | dentro do `try` (vira indeterminado) |
| 4 BAIXA mensagem "política restrita" enganosa | mensagem pelo motivo da sonda |
| 5 BAIXA host POSIX cai no ramo non-admin | igual ao comportamento antigo; nota no guia (usar `bootstrap.sh`) |
| 6 BAIXA textos envelhecidos | `behaviors/manifest.json` e comentário de `tools/test_squad_gate.py` atualizados; ADR-115 é registro histórico, fica como está (a emenda do ADR-047 é a fonte nova) |
| 7 BAIXA regravação reformata o arquivo | limite declarado no guia |
| 8 BAIXA temporário órfão se o processo morrer | nota: janela de milissegundos; `.gitignore` não alterado |

Prova final: `tools/test_nonadmin.py` 23 de 23; 12 de 12 sabotagens.

## 5. Critério de aceite

1. Teste funcional novo em `tools/test_nonadmin.py` cobre C1–C5 em pasta temporária.
2. Sabotagem: restaurar a cópia por cima do `settings.json` faz o teste reprovar (C5); remover a preservação de chaves faz reprovar (C2); escrever sobre JSON inválido faz reprovar (C4).
3. Bateria `python tools/run_canaries.py` sem FAIL novo.
4. Documentos coerentes: docstring do `bootstrap.py`, `guia/MODO-NON-ADMIN.md` (opções B e C), `guia/SETUP.md`, `_doc` do `settings.nonadmin.json`, emenda no ADR-047, CHANGELOG.
5. `python bootstrap.py` no clone canônico deixa `git status .claude` limpo.
