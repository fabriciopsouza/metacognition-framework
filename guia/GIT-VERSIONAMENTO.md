# GIT E VERSIONAMENTO

> Como versionar o framework (e projetos que o usam) com git, alinhado ao SemVer
> que o CHANGELOG adota.

## Inicializar
```bash
cd <pasta-do-framework>
git init
git add .
git commit -m "chore: framework metacognitivo v1.4.0 (base)"
```
O `.gitignore` já ignora segredos, `.env`, credenciais e `.agent/brain/`.

## SemVer — a regra (a mesma do CHANGELOG)
- **MAJOR** (x.0.0): quebra de compatibilidade.
- **MINOR** (1.x.0): feature nova compatível (ex.: novo subagente, novo guia).
- **PATCH** (1.0.x): correção sem feature nova.
> Regra de ouro: o número no nome do release/tag = o número no topo do `README.md`.

## Conventional Commits
```
feat:     nova capacidade        → bump MINOR
fix:      correção               → bump PATCH
docs:     só documentação
refactor: reestruturação interna
chore:    manutenção (build, deps)
```
Exemplo: `feat: adiciona subagente explorer (read-only)`

## Branches
```
main            estável, sempre release-able
feat/<nome>     desenvolvimento de feature
fix/<nome>      correção
```
Fluxo: branch → commits → PR/merge em main → tag de release.

## Marcar um release (tag)
```bash
git tag -a v1.4.0 -m "Repo 100% flexível + drift fix + consolida PROMPT-CHAT-WEB na raiz"
git push origin main --tags
```
A tag deve casar com a versão do `README.md` e a entrada do `CHANGELOG.md`.

## Ao subir versão — checklist
- [ ] Atualizou o número no `README.md`
- [ ] Adicionou bloco no `CHANGELOG.md` (mudança → fonte)
- [ ] Commit `feat:`/`fix:` conforme o tipo
- [ ] Tag `vX.Y.Z` criada e empurrada
- [ ] Nome do .zip (se distribuir) = vX.Y.Z
- [ ] Revisar e, se necessário, atualizar `PROMPT-CHAT-WEB-v4.x.md` na raiz — ele
      parte dos mesmos princípios e busca os mesmos resultados do núcleo. Bump
      da versão do prompt (v4.3→v4.4…) quando mudar.
- [ ] Revisar `## Aprendizado` do `history.md` (ADR-007 / ex-G9): se um mesmo
      padrão de fracasso aparece ≥ 3 vezes, propor ADR que destile a lição em
      skill/regra — antes de fechar o release.

## Nunca comitar
Segredos, `.env`, credenciais, `.agent/brain/` (já no `.gitignore`).
Se vazou um segredo: rotacione a credencial — remover do histórico não basta.
