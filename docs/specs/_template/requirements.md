# requirements.md — Especificação Atômica de uma Feature/Caso

> Clonar esta pasta para cada feature/caso: `docs/specs/<nome>/`.
> Fonte do método: pesquisa A2 (camada atômica do SDD). Esta é a **intenção**,
> não a implementação — não ditar classes/libs aqui.

## Identificação
- **Caso/feature:** <nome>
- **Indicador/objeto:** <o que se analisa ou constrói>
- **Recorte:** <ano | regional | total | n/a>
- **Confiança da tarefa:** ALTA | MÉDIA | BAIXA  → governa o roteamento (ver `rules/04`)

## Escopo funcional (EARS — opcional, mas recomendado)
- **Ubíquo:** "O sistema DEVE <comportamento>."
- **WHEN:** "QUANDO <evento>, o sistema DEVE <resposta>."
- **IF/THEN:** "SE <condição de exceção>, ENTÃO o sistema DEVE <tratamento>."
- **WHERE:** "ONDE <contexto específico>, o sistema DEVE <variação>."

## Fluxos de exceção e lógicas limítrofes (explícitos)
- <NULL / zero / negativo / extremo / string vazia — como tratar>
- <divergência de fonte / dados ausentes>

## Fora de escopo (anti-spec gigante)
- <o que este caso NÃO cobre>

## Fontes de dados
- <tabela/dataset/arquivo + como acessar — file-first antes de assumir colunas>

## Glossário relevante
- <termos deste caso; remeter a 00-glossario.md>
