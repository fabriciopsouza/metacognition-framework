# Execution-report — bloco "Programa de IA Responsável · Natulab" (ADR-038/052 · tier OWNER · privado)

- **Sessão:** 11–12/09/2026 · **Repo de trabalho:** `natulab-ia-estrategia` (externo ao núcleo)
- **Rota declarada:** multi-etapa → squad + `high-stakes-gate` (farmacêutica regulada, decisão executiva)
- **Modelo:** executor **Fable** (autorizado explicitamente pelo dono), QA adversarial **Opus isolado**
- **Tokens (transcripts, ADR-026):** input 54.254 + output 9.244.122 = 9.298.376
- **Arquivos tocados:** 8 documentos de projeto + 5 de evidência + 1 registro de QA; **8 commits**
- **Rodadas de retrabalho:** 1 (v0.1 → v0.2, após REPROVAR do crítico)

---

## Placar gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Material de origem: diagnóstico de maturidade publicado sem medição | **Autor**, na leitura file-first | Nenhum — é prosa de terceiro |
| HIPAA no lugar de ANVISA/LGPD | **Pesquisa adversarial** (Fable) | Nenhum |
| "Regra dos 2%" infundada (grep = 0 no próprio relatório citado) | **Pesquisa adversarial** | Nenhum |
| MIT NANDA mede percepção, não P&L — **o autor havia elogiado o dado** | **Pesquisa adversarial** | Nenhum. Auto-correção registrada em `docs/00` ALTA 7 |
| **`README` afirmava classificação C/I/D que não existia em nenhum documento derivado** | **QA adversarial (Opus)** | **NENHUM — e este é o achado do relatório. Ver §Melhorias** |
| Regra de desempate transformava controle em critério de criticidade | **QA adversarial** | Nenhum |
| RDC 658 Art. 127 atribuído a liberação sendo artigo de retenção | **QA adversarial** | Nenhum |
| Régua do diagnóstico com faixas descobertas (média 4,25 sem estágio) | **QA adversarial** | Nenhum |
| Duas perguntas com polaridade invertida subindo a média de maturidade | **QA adversarial** | Nenhum |
| Omissão seletiva da evidência 05 nos entregáveis | **QA adversarial** | Nenhum |
| **Canários sobrescrevem `.claude/boot-proof.json` com fixtures de teste** | **Autor**, ao investigar por que o liveness insistia | **`test_boot_check.py` — o canário É a causa** |

**Leitura do placar:** 10 dos 11 achados vieram de **julgamento adversarial**, não de mecanismo.
Isso é coerente com o que o framework já sabe de si (prosa é o ponto cego) — mas um deles era
**mecanizável**, e é a melhoria proposta abaixo.

---

## Detecção: framework × humano

- **Mecanismo pegou:** nada de conteúdo. O `squad_gate` instalado no projeto novo **deixou o commit
  passar** — como a pendência prioritária já previa: ele depende de `behaviors/manifest.json`, que
  só existe no núcleo. **Evidência de campo para o item prioritário do backlog: o enforcement viaja
  pela metade — a instalação funciona, a exigência não.**
- **Humano/adversarial pegou:** tudo o mais.
- **Liveness (ADR-061) funcionou como projetado:** insistiu num gate sem carimbo, a causa foi
  investigada em vez de assumida, e o resultado foi um defeito real no núcleo.

---

## Gaps (flagados, não silenciados)

1. **[D]** Artigo da RDC 658/2022 que atribui a liberação de lote a uma pessoa — pendência aberta e
   escrita no projeto; não pode circular para a Garantia da Qualidade antes de conferido no DOU.
2. **[D]** Apresentação da ANVISA de 24/12/2025 sobre o Anexo 22 — PDF não extraível; é a prova mais
   direta da premissa central do programa e ficou por ler.
3. A **v0.2 não passou por nova rodada adversarial.** O próximo bloco deve abrir por ela.
4. `projeto.json` do projeto novo foi criado com `estado`/`agentes`/`capacidade` por preencher.

---

## Melhorias do framework (régua §0 — edita existente, não adiciona)

### 1. Canário de auto-afirmação verificável *(o achado do bloco)*

O defeito mais grave da sessão foi o `README` afirmar que **todo documento classificava suas
afirmações** quando havia **zero ocorrências** dos rótulos. O crítico o pegou com um `grep` e uma
contagem — ou seja, **era mecanizável e nenhum gate o procurou**.

A família de defeito é nova e nomeável: **afirmação verificável que o material faz sobre si mesmo.**
Diferente da fabricação em prosa (que é sobre o mundo e não tem oráculo), esta tem oráculo trivial:
o próprio repositório.

**Proposta (edita `test_marketing_claims.py`, não cria arquivo novo):** estender o canário de
alegações para reconhecer o padrão *"todo/toda X está classificado/marcado/documentado"* e exigir
que a contagem correspondente no repositório seja > 0. É a mesma mecânica do teste de números da
vitrine, aplicada a uma classe adjacente.

### 2. `test_boot_check.py` contamina a prova de produção

Já registrado como trabalho aberto (`canario-contamina-boot-proof`). Rodar a suíte sobrescreve
`.claude/boot-proof.json` com fixtures, e o liveness passa a acusar gate inerte depois de o gate ter
rodado. **Mesma classe do ADR-108:** o artefato que prova, contaminado por quem deveria só verificar.

### 3. Paralelismo de subagente precisa de teto

Cinco agentes Fable simultâneos estouraram o limite de sessão do modelo e **os cinco morreram** —
dois já haviam gravado o arquivo, três perderam tudo. Lançar em lotes de dois funcionou. Vale virar
orientação: **em pesquisa web pesada, no máximo dois subagentes do mesmo modelo em voo.**

---

## Boas práticas (reutilizável)

- **`doc_intake` antes de ler**: o `.pptx` de 22 MB tinha **zero texto** — 15 imagens. Descobrir isso
  por ferramenta, e não por suposição, mudou a estratégia de leitura.
- **Instruir o subagente a declarar o que NÃO conseguiu verificar.** Os cinco levantamentos voltaram
  com seção de limitações, e é isso que os torna citáveis. Dois deles declararam cota de busca
  esgotada em vez de preencher o buraco.
- **Dar ao crítico a régua do próprio autor.** O achado C9 ("o caminho legítimo reprova na pergunta 3
  da sua própria regra") só existe porque o crítico foi instruído a aplicar o critério do autor
  contra o autor.
- **Commitar antes de chamar o crítico.** Evitou a classe de incidente já registrada (subagente com
  Bash revertendo trabalho não salvo).
- **Enforcement instalado na criação do projeto**, não depois: `controle_projeto --iniciar` +
  `install_git_hooks --repo` levaram 2 comandos.

---

## Lições por skill (agnósticas — servem a outro projeto)

- **discovery:** perguntar o escopo regulatório **antes** de pesquisar evitou levantar FDA/EU AI Act
  como obrigação — a resposta "não exporta" reordenou o levantamento inteiro.
- **architect:** ao derivar uma regra de uma fonte, marcar **o que é da fonte e o que é derivação
  própria**. A "regra de desempate" caiu porque era invenção apresentada com a autoridade da norma.
- **qa-critic:** o crítico deve receber **a hipótese de onde procurar**, não só o escopo. Apontá-lo
  para "o artefato que o autor derivou sozinho" produziu o achado mais valioso.
- **docops:** quando o material afirma algo sobre si mesmo, a verificação é uma contagem. Fazer a
  contagem **antes** de escrever a frase.
- **pmo:** achado fora do escopo do bloco (o defeito do `boot_check`) foi **registrado e não
  perseguido** — ADR-112 respeitado sem perder o achado.

---

## O que fica para a próxima sessão

Escrito em `~/.claude/trabalhos/natulab-ia-estrategia.md` e em `PROCEDENCIA.md` no projeto.
Teste binário do P14 — *a próxima sessão começa sem perguntar nada?* — **sim**: próximo passo,
pendências `[D]` e estado do QA estão todos escritos.
