# Execution-report — bloco 1 "desconstruir perfilcampeao.com" (ADR-062 · privado)

- **Sessão:** 18/09/2026 · **Repo de trabalho:** `linkedin-diagnostico` (externo ao núcleo; criado
  nesta sessão, privado em github.com/fabriciopsouza/linkedin-diagnostico)
- **Rota declarada:** multi-etapa → squad, com high-stakes parcial (publicidade regulada —
  CDC/CONAR; LGPD no "pesquise contatos"). Discovery conduzido em conversa (surface-and-reconcile
  com 6 tensões; dono respondeu "siga" com os defaults).
- **Modelo:** autor **Fable 5.1** (baseline da sessão) · QA adversarial **Sonnet isolado** (degrau
  abaixo, ADR-110), 2 rodadas, mesmo crítico com contexto preservado (SendMessage)
- **Arquivos:** 12 documentos + 21 evidências com SHA256 · **3 commits** · 1 PR
- **Rodadas de retrabalho:** 2 (r1 REPROVADO com 6 achados; r2 APROVADO-COM-RESSALVAS com 2)

---

## Placar gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| **"Garantia de Resultado por 30 dias" estava no `checkout-*.js` que EU já tinha baixado** — marquei o teor como DESCONHECIDO; contradiz os Termos do próprio site | **QA r1** (um `grep`) | Nenhum. Não existe canário para "evidência baixada e não lida" |
| **Teste A/B de preço** (R$ 47 "de 97" × R$ 97 "de 249", hash FNV-1a, corte 12/09) no `bundle.js` já baixado | **QA r1** | Nenhum |
| 4 páginas legais + RDAP/ipinfo/DNS/headers citadas como "capturadas" sem estar no repo | **QA r1** | Nenhum — o critério de evidência estava escrito na linha 4 do dossiê e eu mesmo o violei |
| Veredito jurídico "ENGANOSO" com fonte legal não lida | **QA r1** | Nenhum |
| "~50% mais entrega para Reels recentes" — número que o resumo de busca atribuía a uma página **que não o contém** | **QA r1** (pediu fonte 1:1) → **autor** ao reler a página | Nenhum. É o modo de falha da [[fabricacao-em-prosa-e-o-ponto-cego]]: o número veio do resumidor de busca, não da fonte |
| Chamei de "cascas SPA" HTMLs que vêm pré-renderizados (erro introduzido NA correção da r1) | **QA r2** (abriu os bytes; meu grep tratava os arquivos como binário por acentuação) | Nenhum |
| Site usa como marca o termo oficial do LinkedIn ("Perfil Campeão" = All-Star) | **Autor**, por busca | — |
| E-mails de contato/LGPD em domínio que não resolve | **Autor**, por DNS | — |

**Leitura:** 6 de 8 achados vieram do crítico isolado, e **dois deles estavam em arquivos que eu
já tinha em disco**. O padrão é o mesmo do `mutacao-propria`: baixar evidência dá a sensação de
ter lido. O `grep -a` faltando (arquivos com acento lidos como binário) escondeu texto de mim e
não do crítico, que leu em Python.

---

## Melhorias (aprendizado transferível)

1. **Evidência baixada e não grepada = não baixada.** Regra operacional proposta para o
   developer/explorer: depois de arquivar HTML/JS, rodar um `grep -a` por termos-chave do que se
   vai afirmar (preço, garantia, reembolso, CNPJ, e-mail) **antes** de escrever "DESCONHECIDO".
   *Mecanismo candidato (régua §0 — editar, não criar):* o `doc_intake.py` já chunca documentos;
   estender para aceitar HTML/JS e emitir a lista de strings monetárias/legais encontradas.
2. **Resumo de busca não é fonte.** O "~50%" nasceu do resumidor do WebSearch. Número só entra
   com a página lida e a frase literal citada — exatamente o que o repo cobra do site estudado.
3. **`grep` em Windows sem `-a` mente por omissão.** Arquivos com UTF-8 acentuado viram "Binary
   file matches" e o resultado parece vazio. Duas frentes do dossiê dependeram disso.
4. **Uma parada = commit → PR → merge** (dono, 18/09, reforço da memória
   `git-pr-flow-vs-direct-main`): repo novo sobe para o GitHub na hora, não fica local.

## Boas práticas confirmadas

- Commitar antes do qa-critic; crítico read-only por instrução; original intacto nas 2 rodadas.
- Rodada 2 com o **mesmo** crítico (contexto preservado) verificou cada correção na fonte, não na
  prosa — e pegou o erro que a correção introduziu.
- Declarar a remoção do número não confirmado em vez de apagar em silêncio (o crítico apontou
  isso como boa prática).
- Surface-and-reconcile antes de agir: "pesquise contatos" virou "contatos da empresa", nunca de
  usuários; "reconstruir" virou "método, não texto/arte/nome".

## Gaps declarados

- Meta Ad Library bloqueia o agente (403) — os anúncios reais do site são tarefa do dono.
- Textos legais (CDC 36/37/49, Decreto 7.962/2013, CONAR Anexo Q) não lidos na fonte oficial
  (Planalto, CONAR, JusBrasil bloqueiam fetch) — todo enquadramento legal está INFERIDO.
- Modelo de IA e prompts do site: server-side, DESCONHECIDO.
- DNS do `.com.br`: 1 resolver, 1 dia (crítico reconfirmou com 8.8.8.8 e 1.1.1.1, fora do repo).

## Próximo passo

Bloco 2 (architect) com gate do dono: nome do serviço, ticket, stack, funil gratuito como
aquisição. Registrado em `trabalhos.py` (`linkedin-diagnostico-perfilcampeao`).
