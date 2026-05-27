---
papel: discovery
sub_modo: pesquisa-cascata
pergunta_principal: "<pergunta de fundo que destrava a spec>"
rodadas: <1 ou 2>
data: <YYYY-MM-DD>
status: rascunho | revisado | fechado
---

# Research Brief — <Tópico>

> Template do output obrigatório do sub-modo `pesquisa-cascata` (G1 / ADR-007).
> Clonar este diretório (`docs/specs/_template-research/`) para
> `docs/specs/<nome-do-tema>/` e preencher.

## 1. Pergunta principal

<Pergunta de fundo a responder. Concreta o suficiente para guiar a busca.>

## 2. Decomposição (3-5 sub-perguntas multi-hop)

1. <sub-pergunta 1>
2. <sub-pergunta 2>
3. <sub-pergunta 3>
4. <sub-pergunta 4 — opcional>
5. <sub-pergunta 5 — opcional>

## 3. Fontes consultadas

| Fonte | Tipo | Autoridade | Relevância | Acessada via |
|---|---|---|---|---|
| <link/path> | doc oficial / paper / blog / repo | alta / média / baixa | direta / lateral | explorer |
| ... | | | | |

## 4. Achados classificados

### CONFIRMADO (alta confiança, fonte direta)
- <achado 1> — Fonte: <ref §X>
- ...

### INFERIDO (cruzamento de fontes ou raciocínio sólido sem prova direta)
- <achado 2> — Base: <fontes cruzadas + lógica>
- ...

### DESCONHECIDO (lacuna explícita)
- <lacuna 1> — Sugestão de validação: <onde/como obter>
- ...

## 5. Gaps críticos (bloqueiam decisão de spec)

- <gap 1>: <impacto> · <plano de mitigação ou validação>
- ...

## 6. Ataque anti-raso (R3 do intake — obrigatório)

Persona read-only ataca os achados antes do fechamento. Registrar perguntas-ataque e respostas:

| Pergunta adversarial | Resposta / Mitigação |
|---|---|
| Há lacuna não declarada? | <sim/não — qual> |
| Viés de confirmação? | <fonte oposta consultada?> |
| Fonte fraca? | <robustez/alternativa> |
| Alternativa rejeitada sem registro? | <qual + razão> |
| ... | ... |

## 7. Recomendação ao orquestrador

Escolher UMA:

- **Continuar para spec via `discovery` (método universal)** — pergunta principal respondida; `requirements.md` é o próximo artefato.
- **Enviar direto ao `architect`** — achados são suficientes para decisão arquitetural; ADR é o próximo artefato.
- **Mais elicitação** — pergunta principal não foi respondida (gaps críticos restantes); rodar nova rodada de pesquisa-cascata (até N=2) ou voltar ao usuário.

## 8. Metadados

- **Rodadas executadas:** <1 ou 2 — limite hard do passo 5 do algoritmo>
- **Falhas do explorer:** <sub-perguntas que retornaram vazio + tratamento>
- **Tempo de elaboração:** <opcional>
- **Próximo papel:** <discovery | architect>
