# Validation — v1.14.0 Contrato mínimo de skill (gate binário)

> qa-critic valida cada critério VERDADEIRO/FALSO. PASS do bloco = todos VERDADEIRO.

| # | Critério | Como verificar | V/F |
|---|---|---|---|
| V1 | `python tools/validate_skills.py` retorna exit 0 (todas PASS) | rodar o comando | — |
| V2 | As 7 skills têm os 8 campos obrigatórios com dado real | inspeção + V1 | — |
| V3 | `name` de cada skill = nome da pasta e casa `^[a-z0-9-]+$` | V1 (pattern) | — |
| V4 | `shared_refs` aponta para arquivos existentes em `_shared/` | grep dos paths | — |
| V5 | `role_order` único e contíguo 0–5 para a cadeia; explorer=null | inspeção | — |
| V6 | `pass_criteria` de cada skill é binário (sem "talvez/idealmente") | leitura adversarial | — |
| V7 | Schema rejeita campo não-permitido e campo obrigatório ausente | teste negativo (skill fake) | — |
| V8 | Nenhuma skill perdeu conteúdo de corpo (só ganhou frontmatter) | git diff só adiciona frontmatter | — |
| V9 | Campos legados (`source`/`last_review`) não causam FAIL | V1 sobre skill com legado | — |
| V10 | Régua §0: diff não cria camada/arquivo supérfluo; cada campo tem gate | revisão do PC | — |

## Teste negativo (V7) — obrigatório
Criar skill fake em `/tmp` faltando `pass_criteria` e com campo `foo: bar` → validador deve FAIL
com as 2 mensagens. Remover após teste.
