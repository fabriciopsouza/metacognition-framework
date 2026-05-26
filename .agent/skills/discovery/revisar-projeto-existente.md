# Sub-modo "revisar projeto existente" — discovery v1.5.0

> **Companion da `.agent/skills/discovery/SKILL.md`.** Carregar SOB DEMANDA
> quando o filtro de entrada deste sub-modo ativar. Padrão: progressive
> disclosure (ADR-003).

## Quando ativar este sub-modo
Quando a entrada é um sistema que já existe (não uma ideia nova).

### Filtro de entrada
- **ATIVA quando:** sistema que já existe; relatório do explorer disponível; pedido explícito de auditoria/saneamento; refatoração/limpeza de código legado.
- **NÃO ATIVA (REDIRECIONAR) quando:** pedido de feature nova → método universal padrão; processo de negócio → use sub-modo "mapeamento de processo"; jornada UI → trilha web/produto; runbook técnico → developer/docops.

### Passos (downstream — preservado da v1.5.0)
1. Delegar a varredura ao **explorer** (read-only) — mapa, órfãos, duplicação.
2. Sobre o relatório do explorer, conduzir a elicitação: o que sanear, profundidade
   (superfície × refatorar), e **exigir baseline golden** se for mexer em lógica.
3. Produzir o requirements.md do saneamento com critério de aceite =
   "comportamento idêntico ao golden + critérios de limpeza atingidos".
