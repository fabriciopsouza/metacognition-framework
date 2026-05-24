# requirements.md — AIVI: recálculo/análise de indicador (SCAFFOLD)

## Identificação
- Caso/feature: AIVI — análise pontual de indicador a partir de dados brutos
- Indicador/objeto: <PENDENTE — qual indicador? limites/batentes?>
- Recorte: período | regional | total
- Confiança da tarefa: BAIXA (premissa: emergencial/decisão sensível) → reflexivo

## Escopo funcional (EARS) — a preencher com as regras reais
- WHEN <dado bruto recebido/consultado>, o sistema DEVE <validar schema e analisar>.
- IF <condição emergencial — DESCONHECIDA>, ENTÃO DEVE <ação — DESCONHECIDA>.

## Fluxos de exceção
- NULL / zero / negativo / extremo: tratar conforme `_shared/output-format`.
- Total ≠ Σ regionais: reconciliação obrigatória (falha = análise inválida).
- Divergência de fonte / dado ausente: reportar, não silenciar.

## Fora de escopo
- Construção de dashboard; decisão de arquitetura; escrita em sistema de origem.

## Fontes de dados
- <PENDENTE: qual sistema/dataset (via MCP) ou qual arquivo>. File-first antes de assumir colunas.

## ⚠️ Bloqueio
Regras de domínio ('AIVI emergencial', limites/batentes, recálculo) = [DESCONHECIDO].
