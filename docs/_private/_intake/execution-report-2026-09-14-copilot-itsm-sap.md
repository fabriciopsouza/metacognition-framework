# Execution-report — bloco "substrato + RAG interno para agente SAP" (ADR-062 · privado)

- **Sessão:** 13–14/09/2026 · **Repo de trabalho:** `copilot-itsm-sap` (externo ao núcleo)
- **Rota declarada:** multi-etapa → squad + `high-stakes-gate` (licença de terceiro,
  confidencialidade de cliente, material que vai a decisão comercial)
- **Modelo:** autor **Opus** (default) · QA adversarial **Sonnet isolado** (degrau abaixo, ADR-110)
- **Arquivos tocados:** 24 versionados · **5 commits** · canário 15 → 63 checagens
- **Rodadas de retrabalho:** 3 (todas REPROVAR do crítico isolado)

---

## Placar gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Objeto Z minúsculo evadia a classificação (regex sem `re.I`) | **QA adversarial r1** | Nenhum |
| **Índice guardava tokens do corpus em texto claro** — e a doc afirmava o contrário em 4 lugares | **QA adversarial r1** | Nenhum. O canário existia e era **decorativo** |
| CPF/CNPJ sem máscara e e-mail ofuscado evadiam | **QA adversarial r1** | Nenhum |
| `marcadores.json` ausente desligava a proteção em silêncio | **QA adversarial r1** | Nenhum |
| `ztabela` (minúsculo sem dígito) ainda evadia — buraco encolhido, não fechado | **QA adversarial r2** | Nenhum |
| **Teste do aviso era `isinstance(aviso, str)` — sempre verdadeiro** | **QA adversarial r2** | Nenhum |
| `Z-MM0042`, `Z MM0042`, `customZMM0042`, `Z1` evadiam (separador) | **QA adversarial r3** | Nenhum |
| **`ZONE` maiúsculo herdava isenção da palavra comum `zone`** | **QA adversarial r3** | Nenhum |
| Trilha de auditoria reportava CPF/CNPJ "franken" inexistente no texto | **QA adversarial r3** | Nenhum |
| Regressão: `re.I` esquecido ao reescrever o padrão principal | **Canário** (7 testes caíram no mesmo minuto) | **O canário — funcionou** |
| Segundo "CPF" citado pelo crítico não era CPF válido | **Autor**, ao verificar em vez de aceitar | Nenhum |

**Leitura do placar:** 9 de 11 achados vieram de julgamento adversarial. O único achado pego por
mecanismo foi uma **regressão minha**, no minuto em que a escrevi — que é exatamente o que um
canário deve fazer. E um achado do crítico estava factualmente errado: aceitar relatório de
subagente sem conferir teria propagado o erro.

---

## Melhorias (o que o bloco deixa de aprendizado transferível)

1. **Asserção que não pode falhar não é teste — e escrever a lição não impede cometê-la.**
   Registrei no comentário do canário que *"asserção que nunca pode falhar é uma frase"* e, na
   mesma sessão, escrevi `isinstance(aviso, str)` no teste ao lado. O crítico provou reintroduzindo
   o bug: **zero dos 36 testes caiu**. *Sugestão de mecanismo:* um canário que detecte asserções
   tautológicas óbvias (`isinstance(x, str)` sobre retorno tipado, `x is not None` onde a função
   nunca retorna None) valeria para todo o corpus de testes do framework.
2. **Onde o padrão é aplicado importa mais que o padrão.** Três rodadas furaram a mesma detecção
   porque eu casava regex contra **texto bruto**, onde quem escreve controla a separação. O furo
   migrou: caixa → marca de código → separador. Só fechou ao normalizar antes e ler o alvo por
   três ângulos independentes.
3. **Verificar afirmação contra o artefato, não contra a intenção.** Afirmei em 4 lugares que o
   índice não guardava texto do corpus. O próprio `ingerir.py` dizia o oposto no cabeçalho — eu
   tinha a contradição escrita no repositório e não vi.

## Boas práticas confirmadas

- Commitar **antes** de chamar o qa-critic (memória `qa-critic-git-checkout-destroys-uncommitted`):
  os três críticos copiaram o repo para o scratchpad e o original ficou intacto nas 3 rodadas.
- Medir antes de mudar: a varredura dos 64 vereditos do ledger (chave `problemas`) e dos 3
  documentos do corpus evitou regra que reescrevesse o passado.
- Recusar premissa do dono quando os fatos não a sustentam: as perguntas "quais módulos" e
  "funciona conforme o James" foram respondidas com **nenhum** e **NÃO SEI**, com evidência.

## Gaps declarados

- **Gate de saída é procedimento, não mecanismo.** Depende de alguém rodar `--modo externo`;
  não há verificador que examine o material final (slide/PDF) e barre trecho classificado.
- **Detecção por padrão nunca é completa** — forma de escrita não prevista passa.
- **Colisão de sessões no mesmo repo:** durante o bloco, uma segunda sessão editava o núcleo ao
  vivo (arquivo gravado com `\n` literal quebrado, `SyntaxError` em disco). O framework não tem
  detecção de duas sessões concorrentes no mesmo working tree — o sinal foi indireto (mtime,
  veredito aparecendo sem eu gravar).
- **Rodada 4 do QA não rodou.** A r3 recomendou escalar para ADR por serem 3 reprovações na
  mesma classe; decisão ficou com o dono, que optou por seguir para uso.
