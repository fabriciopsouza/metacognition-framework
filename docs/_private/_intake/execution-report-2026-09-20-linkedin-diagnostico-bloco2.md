# Execution-report — bloco 2 "nome + spec do Perfil Doctor" (ADR-062 · privado)

- **Sessão:** 18–20/09/2026 · **Repo de trabalho:** `linkedin-diagnostico` (privado, GitHub)
- **Rota:** squad (architect); discovery de nome em conversa; dono decidiu por "siga" com as 4
  preferências recomendadas (Perfil Doctor · R$ 47 único · builder · funil grátis = aquisição)
- **Modelo:** autor **Fable 5.1** · QA adversarial **Sonnet isolado**, rodadas 3 e 4 (o mesmo
  crítico das rodadas 1-2, contexto preservado; travou uma vez ao compilar — retomado com
  "entregue o que já tem", sem reler)
- **Arquivos:** 2 novos (`05-produto/nome.md`, `spec.md`) + 7 editados + 1 evidência nova ·
  **4 commits** · 1 PR
- **Rodadas de retrabalho:** 2 (r3 REPROVADO, 9 achados; r4 APROVADO-COM-RESSALVAS, 2)

---

## Placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| CA-2 dizia "11 linhas" numa tabela de 10 | **QA r3** | Nenhum — critério "binário" auto-inconsistente; um `grep -c` no build teria pego, mas o build não existe ainda |
| CA-6 passava com placeholder ("encarregado: a definir") | **QA r3** | Nenhum |
| "Nenhum uso de Perfil Doctor" CONFIRMADO com 1 busca — **mesmo overclaim que a r1 já tinha corrigido noutro arquivo** | **QA r3** | Nenhum. Lição aplicada num arquivo não migrou para o próximo |
| Critério 1 "lia" foto do PDF; critério 4 usava LLM como se fosse determinístico | **QA r3** | Nenhum |
| Retenção 12 meses × 30 dias contradizia | **QA r3** | Nenhum |
| Divisão por zero no critério 2 | **QA r3** (checklist `output-format`: DIV/0) | O checklist existia e eu não o rodei na spec |
| "registro.br bloqueia RDAP" era falso — **faltava o header `Accept`** | **QA r3** (teste ao vivo) | Nenhum. Consequência: **`perfilcampeao.com.br` está registrado desde 03/2026 por pessoa física** e a r1 dizia "domínio inexistente" |
| "Estacionado" era generoso: a delegação não responde nem o apex | **QA r4** (consultou o NS de parking direto) | Nenhum |
| Resíduos "não resolve"/"inexistente" e **IP do consultante** no JSON do RDAP | **Autor**, varredura própria entre rodadas | Nenhum |
| PII do titular (nome, e-mail, CPF, `legalRepresentative`) no JSON baixado | **Autor** — redigi antes de commitar; **o primeiro passe deixou `legalRepresentative`** (campo fora do vCard) e só o `grep -c` de conferência pegou | Nenhum canário de PII em evidências |

**Leitura:** 8 de 10 vieram do crítico; 2 da minha varredura. O mais importante não foi achado de
spec — foi de **infra da rodada 1**: um header HTTP errado virou a afirmação "domínio inexistente",
que sobreviveu a duas rodadas de QA porque o crítico e eu reproduzíamos o mesmo erro (403 sem
`Accept`). Só caiu quando o crítico testou por outro caminho.

## Melhorias

1. **Erro de ferramenta vira fato.** 403 do RDAP foi lido como "bloqueado" e o "bloqueado" virou
   "não existe". Regra: resposta de erro de API nunca sustenta afirmação sobre o mundo — só
   "não consegui consultar". Candidato a linha no `anti-hallucination` (editar, não criar).
2. **Lição corrigida num arquivo tem de ser grepada nos outros.** A r1 rebaixou "nenhum encontrado
   → na busca feita"; eu escrevi o mesmo overclaim em `nome.md` dois dias depois. Mecanismo barato:
   ao corrigir classificação, `grep -rn "CONFIRMADO — busca"` no repo inteiro.
3. **Redação de PII precisa de 2º passe fora do schema.** Redigi o vCard e o `publicIds`; o
   `legalRepresentative` estava em outro nível do JSON. Regra: depois de redigir por estrutura,
   `grep` pelos valores reais (nome, e-mail, dígitos) — foi o que pegou.
4. **Checklist `output-format` (DIV/0, NULL) vale para spec, não só para código.** O critério 2
   era uma porcentagem sem guarda de denominador; o checklist já cobria isso.
5. **Crítico travado: pedir a saída, não reler.** O agente parou ao compilar; "entregue o que já
   levantou" recuperou o relatório completo em 1 turno.

## Boas práticas confirmadas

- Mesmo crítico nas 4 rodadas (SendMessage) verificou correções **na fonte** e pegou o erro que
  a correção introduziu (r2) — o contexto preservado paga.
- Atribuição honesta: `nome.md` credita ao crítico o `resumedoctor.com` e admite meu timeout.
- Minimização por decisão própria: titular do `.com.br` é pessoa física → redigido, com o caminho
  público (RDAP) indicado para o dono. Não perguntei — é regra 3 do repo.
- Cada parada = commit → PR → merge (regra do dono de 18/09), sem esperar pedido.

## Gaps declarados

- Textos legais (CDC 36/37/49, Decreto 7.962/2013, CONAR Anexo Q, CTN p/ 5 anos): Planalto,
  normas.leg.br, CONAR, JusBrasil bloqueiam fetch — **todo enquadramento legal está INFERIDO**.
- INPI (classes 35/42), `@perfildoctor`, registro.br, Meta Ad Library: só o dono.
- Limiares 70/40 % do critério 2: calibrar com uso.
- `resumedoctor.com`: confirmado pelo crítico, meu `curl` deu timeout.

## Próximo passo

Bloco 3 — dev no builder (Lovable + Supabase + Mercado Pago) contra os 10 critérios de aceite da
spec; bloco 3b aquisição. Ledger: `linkedin-diagnostico-perfilcampeao`.
