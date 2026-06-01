# Teste isolado do framework num caso de domínio real (sem vazamento)

> Como validar, **de campo**, se o framework produz o resultado premium **com menos interações** —
> sem que o domínio do caso vaze para o framework (ADR-010, anti-vazamento cross-sessão).

## Por que funciona (isolamento estrutural, não disciplinar)

| Fronteira | Onde fica | Isolamento |
|---|---|---|
| **Framework** | clone do **público** (`mfw-clone`) | prova que o distribuído funciona **e** não carrega cliente |
| **Projeto do caso** | pasta separada (`teste-isolado/`), **git próprio** | commits/artefatos nunca tocam o framework |
| **Memória** | `~/.claude/projects/<slug-do-cwd>/` | o slug deriva do **cwd** → pasta de teste = memória separada (automático) |

A regra de ouro: a sessão do caso roda com **`cwd` na pasta do projeto**, nunca dentro do clone do framework.

## Uso (1 comando)

```powershell
# 1. setup: clona público + bootstrap + projeto isolado com seus dados
pwsh ./guia/teste-isolado.ps1 -DataSource "C:\caminho\dos\dados"

# 2. abra o Claude Code com cwd = a pasta de teste (o script imprime o caminho + um prompt pronto)

# 3. depois do teste: prova que NADA do domínio vazou de volta para o framework
pwsh ./guia/teste-isolado.ps1 -LeakCheck
```

## O que observar (acceptance)
- **Menos interações:** o discovery deve **propor o produto premium de uma vez** (blueprint) — você
  confirma/ajusta, em vez de empurrar requisito a requisito.
- **Validação de arquivos:** `check_input_contract` deve detectar+validar os arquivos de `./dados`.
- **GUI premium:** o ux-gate (launcher/leigo/estados) deve barrar GUI básica.
- **Zero vazamento:** `-LeakCheck` deve dar `--sensitive` verde + git limpo no clone do framework.

> O caso de domínio é **do projeto**, nunca do framework. Se for um caso novo recorrente, registre o
> token dele em `tools/sensitive-denylist.txt` **antes** de dogfoodar (o gate não protege o que não conhece).
