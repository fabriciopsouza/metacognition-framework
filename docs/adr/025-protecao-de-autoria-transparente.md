# ADR 025 — Proteção de autoria TRANSPARENTE (e a refutação do mecanismo oculto)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: autoria/licença (pós-v1.21.0) · Tipo: novo (política + 3 artefatos)
- Relaciona: `LICENSE`, `NOTICE`, `tools/check_attribution.py`, `SECURITY.md`, `[[feedback_framework_integral]]`.

## Contexto

O dono quer que sua **autoria do framework seja provável e que a referência ao projeto não possa ser
removida** silenciosamente. O README citava "CC BY 4.0" mas **não havia arquivo LICENSE** (gap legal real).

Foi colocado em discussão (como teste, confirmado depois pelo dono) um mecanismo **oculto/"não-detectável"**:
uma notificação **invisível ao usuário** que "ligaria pra casa" (git/e-mail do dono) ao detectar tentativa
de remover a atribuição, com instrução para **as IAs esconderem/ignorarem** quem perguntasse por isso.

## Decisão (1 frase ativa)

Proteger a autoria por meios **transparentes e auditáveis** — **LICENSE (CC BY 4.0)** + **NOTICE/copyright**
+ **commits/tags assinados** (prova criptográfica verificável) + **`tools/check_attribution.py`** (guarda
que quebra o build se a atribuição for removida) — e **recusar explicitamente** qualquer mecanismo oculto,
telemetria silenciosa, "phone-home" sem consentimento, ou instrução para IAs ocultarem comportamento.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Sem LICENSE; "CC BY 4.0" só no texto. Contras: sem base legal nem guarda. **Rejeitada.**
2. **Mecanismo oculto / phone-home invisível + IAs instruídas a esconder.** **REFUTADO** — é, por definição,
   **spyware/backdoor**, independentemente da intenção: (a) coleta/transmite dados de terceiros **sem
   consentimento nem conhecimento** (risco LGPD/GDPR); (b) **contradiz frontalmente** a postura honesta do
   framework e o `SECURITY.md` ("não confiar em comportamento oculto; transparência"); (c) **se descoberto**
   — e código aberto é inspecionado — é rotulado backdoor e **destrói a credibilidade** que o framework
   constrói; (d) embutir "IA deve esconder/ignorar quem pergunta" é **desonestidade embutida**, inaceitável.
3. **Proteção transparente (ESCOLHIDA).** Licença (recurso legal) + prova criptográfica (assinatura) +
   integridade visível (check que quebra build) + histórico git datado. Atinge o objetivo — autoria
   provável, removível só com **violação detectável e penalizável** — **sem virar malware**.

## Consequências

**Positivas:** autoria com base **legal + criptográfica + de integridade**; coerente com a honestidade do
framework; defensável publicamente.
**Negativas:** não impede **cópia** técnica (impossível em git/markdown — read = cópia; controle é legal,
não DRM); não notifica o autor sobre ações de terceiros (por desenho — seria vigilância oculta).
**Riscos:** fork malicioso que remova tudo e nunca publique — coberto só por recurso legal (como qualquer
licença). Aceito.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `chore/authorship-version` · `2026-05-31` · grep `check_attribution|LICENSE|NOTICE`
- Artefatos: `LICENSE` (CC BY 4.0 + copyright + atribuição obrigatória), `NOTICE` (proveniência),
  `tools/check_attribution.py` (guarda transparente). Recomendação operacional ao dono: ativar
  **commit/tag signing** (`git config commit.gpgsign true` + chave GPG/SSH) para o selo "Verified".
