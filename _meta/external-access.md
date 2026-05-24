# External Access — Padrão de Conectividade (genérico)

> Como o framework acessa **qualquer** sistema externo (banco, API, data warehouse,
> planilha, serviço). Vendor-agnóstico. Fonte: pesquisa A2 (tabela de decisão
> Skill vs Subagente vs MCP vs Slash).

## Princípio: "a skill diz COMO; o MCP conecta"
O conhecimento de *o que fazer* mora numa skill (genérica ou de aplicação). A
*conexão* ao sistema externo mora num **MCP server** — credenciais geridas fora do
prompt, contrato padronizado.

## Quando usar o quê
| Situação | Use |
|---|---|
| Injetar especialização na conversa atual (output curto, usa o contexto do usuário) | **Skill** |
| Acessar sistema externo (banco, API, warehouse, arquivo remoto) | **MCP** |
| Trabalho longo/ruidoso/paralelizável sobre dados externos | **Subagente** (`explorer`) + MCP |
| Atalho determinístico do usuário | **Slash command** (pode encadear skill+MCP) |

## Regras genéricas de acesso (independem do sistema)
1. **Credenciais nunca no prompt** — sempre via config do MCP/env.
2. **File-first / schema-first** — inspecionar o esquema real antes de assumir
   campos (`_shared/traceability`).
3. **Validar o que volta** — checar contra schema esperado antes de usar
   (`_shared/output-format`).
4. **Rastrear a origem** — todo dado externo carrega sua fonte/versão
   (`_shared/traceability`); em alto risco, log imutável (`_shared/observability`).

## Como uma aplicação concretiza
A aplicação (clone de `_template`) declara **qual** MCP server usa e **qual** schema
espera. O núcleo só define o padrão. Nenhum nome de produto vive no framework.
