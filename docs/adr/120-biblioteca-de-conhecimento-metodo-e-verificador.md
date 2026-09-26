# ADR-120 — Biblioteca de conhecimento: método de construir e consultar, modelo e verificador

- **Status:** Aceito
- **Data:** 2026-09-26
- **Decisores:** dono (Fabricio). Plano B3, decisão D9 (26/09). Pedido de 26/09 de consultas reutilizáveis entre
  projetos (débito DB1), com respostas D1–D6. Ordem de 26/09: "siga no plano", depois de o autor apontar que o
  DB1 duplicava o D9. Ordem de 26/09: trabalhar só no agnóstico ("o MÉTODO"). Autoria: Opus 5.5.
- **Relação:** executa o B3e do plano `docs/specs/b3-documentacao-regulada/spec.md` (REQ-16 a REQ-18,
  critérios 17 a 19). Reusa o `knowledge_catalog` (ADR-068, BM25), o arquivo único (ADR-117), o banco de dimensões
  (ADR-033) e a regra global (ADR-116). Quita o débito DB1 (`docs/_backlog/gaps-otimizacao.md`) na parte agnóstica.

## Contexto

1. Consultas, fatos medidos e termos confirmados num projeto eram refeitos em outro, porque cada um vivia só na
   pasta do projeto que o criou.
2. O D9 já tinha aprovado um dicionário por perfil, empresa e projeto, com relações e índice de projetos.
3. "Consultar antes" escrito como prosa não segura, e o framework tem casos registrados disso.
4. O framework já tem uma busca (`knowledge_catalog`); uma segunda criaria duas respostas para a mesma pergunta.

## Decisão

1. **Modelo agnóstico** em `exemplos/conhecimento/_modelo/`, com a estrutura:
   - `perfis/<p>/DICIONARIO.md`;
   - `empresas/<e>/DICIONARIO.md`;
   - `empresas/<e>/<área>/<assunto>.md`;
   - `INDICE-PROJETOS.md`;
   - `conhecimento.json`.

   Entrada é um bloco `## <nome>` com campos fixos. Os tipos são termo, consulta, fato, pesquisa e runbook. O
   README do modelo é o método (POP), com as seções consultar, construir e quando refazer.
2. **Validade por classe:**
   - estrutura: até mudar a versão do sistema declarada em `conhecimento.json`;
   - configuração: 6 meses;
   - regra de negócio e conceito: 12 meses;
   - retrato (número medido): não vence e é citado sempre com a data;
   - qualquer classe: **Contestado em:** vira "a reverificar" na hora.
3. **`tools/conhecimento.py`:**
   - `verificar` acusa: campos obrigatórios por tipo; data inválida ou no futuro; confiança "CONFIRMADO" sem quem;
     relação de tipo desconhecido ou para termo inexistente; termo em dois níveis ou repetido; estrutura sem
     sistema e versão, ou com versão atual não declarada; consulta sem texto pronto; formato não reconhecido;
     arquivo fora da estrutura; ponteiro para caminho inexistente; credencial ou documento de identificação;
     índice com caminho inexistente; projeto com trabalho aberto em `trabalhos.py` sem linha no índice;
   - `vencidos` lista o que deve ser refeito.
4. **Uma busca só:** `knowledge_catalog --recall --conhecimento <raiz>` lê a biblioteca ao vivo. Sem a opção, nada é
   carregado. Retrato sai com "em dd/mm/aaaa:".
5. **Método nas peças existentes:**
   - discovery, item 0: consultar antes; perguntar empresa e perfil; termo confirmado entra no ato;
   - docops, passo 7: registrar ao fechar o bloco, ou declarar "nada a registrar";
   - regra global, seção 9, com 2 cláusulas novas no `check_rules_parity`;
   - regra global, seção 6: comando permanente `status` (tabela checklist com % por bloco + 3 linhas),
     pedido repetido do dono em 26/09, mais 1 cláusula (19 no total);
   - dimensão `biblioteca-consultada` no banco com `obr=unico`: obrigatória só no arquivo único de especificação.
     O formato antigo não muda de veredito, e ninguém inventa resposta para especificação anterior à regra.
6. **Instância do dono:** `docs/_private/conhecimento/` (D9), criada vazia de conteúdo. O conteúdo é das sessões de
   domínio.

## Alternativas descartadas

- Plano e estrutura próprios para consultas (primeira versão do DB1): duplicava o D9.
- `conhecimento.py buscar`: segunda busca ao lado do `knowledge_catalog`.
- Dimensão `biblioteca-consultada` obrigatória em todo formato: reprovaria especificações anteriores à regra, e a
  saída seria preencher com texto de exceção copiável.
- Validade só por tempo: não pega mudança de sistema nem contradição.

## Régua §0

Critério (c): o banco de dimensões e o `knowledge_catalog`, que já existiam, passam a medir o que era prosa. Critério
(a): o DB1 foi fundido ao B3e em vez de virar plano e estrutura próprios. Adiciona 1 verificador e 1 canário.

## Prova

- `tools/test_conhecimento.py`: modelo passa; 34 sabotagens reprovam com o achado esperado (6 delas vindas das
  rodadas 1 e 2 do QA); 8 exceções legítimas passam (valor em R$, campo dentro de bloco de código, prosa que
  descreve um campo chamado "token", sub-título só com texto, campo depois do bloco de código da consulta, índice
  com caminho existente, trabalho tratado, trabalho do próprio framework); biblioteca vazia responde "nada
  encontrado" sem erro; vencidos por versão, por prazo e por contestação; retrato não vence; busca devolve a entrada
  com a data; sem `--conhecimento` nada é lido; modelo e verificador sem termo de domínio.
- Mutação do verificador e da busca (script de sessão, não versionado): 38 mutações, 38 mortas. As 2 que
  sobreviveram na primeira passada levaram a um caso novo no canário e à remoção de uma linha redundante.
- `tools/test_spec_unico.py` caso (j): arquivo único sem `biblioteca-consultada` reprova; formato antigo não; a
  equivalência (a)/(b) compara só o contrato comum.
- `tools/test_spec_depth.py`, `tools/test_discovery_eval.py`, `tools/test_knowledge_catalog.py`,
  `tools/test_rules_parity.py` (19 cláusulas), `tools/check_core_agnostic.py`: PASS.

## Limites

- Campos fixos tornam a biblioteca legível por máquina; relações entre termos são as 5 do D9. Não é uma ontologia
  formal.
- O verificador prova forma, rastro e validade, não a verdade do conteúdo.
- Credencial: pega "chave: valor" no fim da linha (com comentário ou anotação), parâmetro de URL e cabeçalho de
  autorização. Segredo no meio de uma frase comum escapa. Afrouxar mais acusaria a prosa que descreve campos.
- A checagem cruzada com `trabalhos.py` acusa todo projeto de domínio com trabalho aberto enquanto o índice estiver
  vazio. É a pendência de preenchimento, das sessões de domínio.
- "Consultar antes" é cobrado pela dimensão só no arquivo único. Em conversa sem especificação, continua sendo
  regra (seção 9 da regra global).

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 3 | Sonnet isolado, segundo plano (a1c73b1fdf84cdf66) | PASS | nenhum: correções da rodada 2 reproduzidas; rodada 1 não reaberta; sem falso positivo de credencial em prosa ("o campo senha: definido pelo usuário (obrigatório)", "token: veja o manual # seção 3") | — |
| 2 | Sonnet isolado, segundo plano (ab523c78962d0b793) | PASS-COM-RESSALVAS | as 6 correções da rodada 1 confirmadas. 1 ALTA nova: campo depois do bloco de código da consulta era acusado e descartado (falso positivo criado pela correção da rodada 1). 1 MÉDIA: "senha: abc123 (trocar)" e "Authorization: Bearer" escapavam | só prosa marca o corpo (código não); credencial aceita comentário/anotação à direita e cabeçalho de autorização; limite declarado; 3 casos novos |
| 1 | Sonnet isolado, primeiro plano (ae8eb988d9d5e2a16) | PASS-COM-RESSALVAS | 2 ALTA: campos antes do 1º `##` sumiam sem achado; entrada com `###` se fundia à anterior. 3 MÉDIA: prosa "o campo token: armazena…" acusada como credencial; rótulo "9/9" no arquivo único com 10 obrigatórias; busca com biblioteca vazia dava erro e mandava rodar `--build`. 1 BAIXA: caminho relativo na seção 9 da regra global | campos no topo da entrada, campo depois do corpo e campo antes do 1º `##` acusados; credencial = valor único no fim da linha ou parâmetro de URL; contagem por especificação; biblioteca vazia responde "nada encontrado" (exit 0); `{{FRAMEWORK_ROOT}}` na seção 9. 6 casos novos no canário |
