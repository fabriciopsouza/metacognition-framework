# Como Revisar Outro Repositório (sem mexer na estrutura)

> Guia rápido. Usa o framework como ferramenta e o repo-alvo como fonte de leitura.
> Nada é copiado nem editado em nenhuma das duas pastas. Read-only por padrão.

## Setup (uma vez, ~30 segundos)
1. Abra a pasta deste framework no VS Code.
2. **File → Add Folder to Workspace** → selecione a pasta do projeto a revisar.
3. (Opcional) **File → Save Workspace As…** → salve como `revisao.code-workspace`
   para reabrir os dois juntos depois com 1 clique.

Resultado: duas raízes lado a lado. O framework lê o `AGENTS.md`/`.agent/` DELE;
o projeto-alvo entra só como fonte. A `.agent/` antiga do projeto-alvo (se houver)
fica inerte e é ignorada — o framework que vale é o desta pasta.

## Abrir a sessão
No Claude Code:
```
/start-session
```
O PMO lê AGENTS.md → .agent/rules/ → briefing.md e abre a sessão.

## Varrer o repo-alvo (read-only) — prompt pronto
Cole no Claude Code, trocando <projeto-alvo> pelo nome da pasta adicionada:

```
Use o explorer para varrer a pasta <projeto-alvo>.
Objetivo: mapear os arquivos .py, identificar as regras de negócio e
as dependências. READ-ONLY — não altere, não corrija, não escreva nada.
Devolva só o destilado: estrutura, regras encontradas (classificadas
CONFIRMADO/INFERIDO/DESCONHECIDO) e o que ficou sem cobertura.
```

O explorer é read-only por design — nunca escreve nem corrige; só reporta.

## Próximos passos conforme o que você quer
- **Só entender o repo** → pare no explorer. O resumo é o entregável.
- **Análise crítica** → `/handoff qa-critic` sobre os achados (busca inconsistências,
  riscos, regras frágeis).
- **Decidir mudança estrutural** → `/handoff architect` (gera ADR).
- **Mudar código** → só então `/handoff developer`. Ele escreve no projeto-alvo
  apenas o que você autorizar; qa-critic valida antes de aceitar.

## Limites honestos
- **Leitura** dos arquivos: livre (basta a pasta estar no workspace).
- **Executar** os .py (não só ler): exige o terminal/ambiente do projeto-alvo.
- **Isolamento real + auditoria**: você está no Claude Code, então o explorer roda
  como subagente isolado de verdade e o hook de `_shared/observability` pode logar
  a revisão em audit-log.jsonl. (Em chat web isso seria só simulado.)

## Encerrar
`/checkpoint` ao fim — grava o resumo da revisão em history.md (rastreável).
Para soltar o repo-alvo: remova a pasta do workspace. Zero resíduo.
