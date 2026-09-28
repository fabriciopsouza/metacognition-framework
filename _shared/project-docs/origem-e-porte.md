> Parte de `_shared/project-docs/SKILL.md` (entrada enxuta desde 28/09/2026, B3c). Conteúdo copiado integral da versão anterior; a entrada aponta para cá.

# Documentação de projeto que sobrevive à troca de dono

> **O que este padrão resolve:** projeto cuja documentação existe, é bonita, e mesmo assim
> obriga quem chega a perguntar tudo de novo — porque o que está escrito não é verificável,
> não tem dono, ou envelheceu sem avisar.
>
> **Origem:** conjunto documental real submetido a revisão adversarial por modelo diferente do
> autor, em 5 rodadas, com **3 reprovações**. Os 6 modos de falha do §5 são os achados que
> barraram o merge — não são hipóteses.

## §0 — Onde esta skill se encaixa

Não substitui os núcleos vizinhos; **instancia** três deles para o caso "documentar um projeto":

- **`confidence-classification`** continua sendo a única definição de origem de afirmação
  (CONFIRMADO · INFERIDO · DESCONHECIDO). Aqui ela ganha um quarto estado de projeto,
  **REFUTADO** (§2.2), e a exigência de que a marca apareça no texto, não só na cabeça de quem
  escreveu.
- **`traceability`** define o rastro. Aqui ele vira exigência de formato: prova com **consulta
  reproduzível** (§2.3).
- **`validation-reporting`** é dona de **validar dado contra uma referência** (campo a campo, com
  níveis por consequência e veredito). Esta skill é dona de **registrar um fato de projeto** com
  rastro. Fronteira: *"os valores conferem com a referência?"* é lá; *"como este projeto guarda o
  que já provou?"* é aqui. O §2.3 usa o formato de prova, não redefine método de validação.
- **`docops`** fecha o *bloco* (CHANGELOG, ADR, execution-report). Esta skill trata do *projeto*.
  Ordem: docops chama esta quando o bloco entrega ou altera documentação de projeto.

**Esta skill é PROSA, não gate.** Não tem canário próprio (registro `project-docs-standard`:
PARTIAL/prose). Ela orienta e é cobrável em revisão adversarial; não bloqueia release. Tratá-la
como bloqueio sem mecanismo seria o teatro de conformidade que o próprio framework proíbe.

**Régua §0 (ganho líquido) se aplica a esta skill também.** O conjunto do §3 é **graduado**:
adotar os 15 arquivos num projeto de duas semanas é o mesmo defeito que esta skill combate.

---
