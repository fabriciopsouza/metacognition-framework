> Parte de `_shared/project-docs/SKILL.md` (entrada enxuta desde 28/09/2026, B3c). Conteúdo copiado integral da versão anterior; a entrada aponta para cá.

## §4 — Gates executáveis (nenhum é opinião)

Documentação sem gate apodrece sem avisar. Todo conjunto declara comandos com resposta objetiva.
Os quatro abaixo são o mínimo; adapte os alvos ao projeto.

1. **Link quebrado** — nenhum documento cita arquivo inexistente. *Esperado: 0.*
2. **Fronteira** — a parte reutilizável não cita o domínio consumidor. *Esperado: 0.*
3. **Anti-duplicação** — um número-chave (contagem de referência, total do conjunto) aparece por
   extenso só no arquivo declarado dono. *Esperado: um arquivo, nem mais.*
   **Cuidado:** contar em quantos arquivos a string aparece é gate SINTÁTICO — ele passa enquanto o
   número já está velho. O gate útil confere o número **contra a fonte viva**, não contra si mesmo.
4. **Verdade contra o mundo** — uma consulta que confere as invariantes do produto contra a fonte
   viva. *Esperado: tudo PASS.*

**O gate precisa listar suas próprias exceções e por quê.** Gate que reprova por motivo legítimo é
desligado por quem tem pressa, e nunca mais volta.

---

## §5 — Os 6 modos de falha já observados

Cada um foi pego por revisão adversarial, não por inspeção do autor.

| # | Falha | Como se manifesta | Antídoto |
|---|---|---|---|
| 1 | **Duplicação que o mapa nega** | O mapa afirma que os outros "apontam"; eles copiam | Gate 3 + §2.1 |
| 2 | **Glossário perdido na consolidação** | Termos somem na reorganização e passam a ser usados sem explicação — violando a regra que os próprios documentos formulam | §2.6 + conferir termos antes/depois de toda consolidação |
| 3 | **Nome sem procedência sob cabeçalho que afirma verificação** | Os nomes até existiam; o defeito era a falta de rastro **sob um título que prometia rastro** | §2.2 — a marca vale para o cabeçalho também |
| 4 | **Junção que não dá erro e devolve resultado corrompido** | Chave incompleta combina linhas de origens diferentes; a consulta roda, o número sai, e está errado | §2.3 — a consulta na prova é o que permite alguém ver a junção |
| 5 | **Corrigir só onde o revisor apontou** | O achado é tratado como incidente, não como classe; o mesmo defeito segue vivo em outros cinco lugares | Ao receber achado, **varrer onde o problema existe**, não onde foi apontado |
| 6 | **Polimento que escapa da revisão** | Mudança "pequena" pós-entrega com superfície estrutural real entra sem crítica | Toda mudança estrutural passa por revisão adversarial, inclusive a que parece cosmética |

**O padrão por trás de 1, 3 e 5 é o mesmo: afirmar sem lastro.** Ele só se quebrou quando consertar
um gate defeituoso revelou sozinho uma sexta duplicação que ninguém tinha pedido para procurar.

---

## §6 — Revisão adversarial: quem, e com que instrução

O conjunto documental **não é aprovado por quem o escreveu**.

- **Revisor ≠ autor.** Modelo diferente, ou pessoa diferente. Auto-revisão encontra erro de
  digitação e não encontra racionalização.
- **A instrução é encontrar defeito, não aprovar.** Hipótese default: existe defeito.
- **Veredito explícito:** aprovar · aprovar com ressalvas · reprovar — com achados e evidência.
- **Regra de escalonamento:** três reprovações seguidas na mesma entrega significam que o problema
  é o **desenho**, não a execução. Pare de iterar e reabra a decisão.

*Evidência de que funciona:* no conjunto que originou esta skill, o revisor reprovou 3 vezes em 5
rodadas, e o achado mais grave (modo de falha 4) estava justamente na consulta usada para provar
uma refutação regulatória.

---
