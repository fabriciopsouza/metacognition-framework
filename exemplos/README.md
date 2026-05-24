# exemplos/ — Aplicações do Framework (NÃO é o núcleo)

> Tudo aqui é **aplicação**: demonstra como o framework genérico encontra um
> domínio/contexto. Nada aqui é necessário para o framework funcionar — são
> referências de "como aplicar", criadas clonando `.agent/skills/_template`.

## O que tem aqui
- `tableau-senior-analyst/` — aplicação a um contexto de BI/visualização.
- `python-fuel-forecaster/` — aplicação a análise/forecasting de dados.
- `regulated-pharma/` — aplicação a contexto regulado (config de `_shared/high-stakes-gate`).
- `aivi-indicator-analyst/` — análise pontual de indicador (SCAFFOLD; domínio pendente).
- `workflows/` — workflows específicos de domínio (sap-change, bi-deliverable).

## Como ler
Cada SKILL.md de exemplo: (1) carrega skills de `_shared/`; (2) adiciona só o
domínio. Troque o domínio e você tem uma aplicação nova (ex.: análise de indicador,
contexto X, contexto Y) sem tocar no núcleo.
