# ADR-119 — Kit regulado: motor neutro, perfil declarado por projeto

- **Status:** Aceito
- **Data:** 2026-09-26
- **Decisores:** dono (Fabricio) — plano B3 aprovado em 26/09/2026 (D1–D9; PR #159); decisão D1:
  *"não teremos perfil regulado padrão, pois também trabalho com ANP/outros. Perfil regulado por
  projeto deve ser solicitado"*. Autoria: Opus 5.5.
- **Relação:** executa o incremento B3a-1 de
  `docs/specs/b3-documentacao-regulada/spec.md` (REQ-01, REQ-03, REQ-04, REQ-08). Reusa ADR-043
  (perfis em `exemplos/dominio-regulado/`), ADR-117 (arquivo único, leitor `spec_fonte`), ADR-116
  (regra global), ADR-020 (núcleo neutro).

## Contexto

1. O dono exige formalização mínima de projeto para ambiente regulado — requisito, risco, teste,
   evidência, rastreabilidade — e trabalha com mais de um órgão (sanitário, petróleo, outros).
2. Não havia verificação executável de rastreabilidade: requisito sem teste, risco alto sem
   mitigação e resultado sem evidência passavam por prosa.
3. O núcleo não pode conter norma (ADR-020); os perfis já moram fora dele (ADR-043).

## Decisão

1. **Partes F (Riscos) e G (Testes e evidências)** no arquivo único (`spec_fonte.PARTES`), sem
   equivalente no formato antigo. Modelo: `docs/specs/_template-spec-unico/spec.md`.
2. **Campos da Parte A:** `**Impacto regulado:** sim|não`, `**Perfil regulado:** <nome>|nenhum`,
   `**Sistema:**`, `**Categoria de software:**`, `**Categoria decidida por:**`,
   `**Requisitos confirmados por:**`. Parte F: risco, requisito, falha, impacto, probabilidade,
   detecção, classe (alto|médio|baixo), mitigação, teste. Parte G: teste, requisito, categoria,
   roteiro, esperado, resultado, evidência, nome e data.
3. **`tools/regulado.py`** — motor sem nome de órgão ou norma; as regras vêm do perfil
   `exemplos/dominio-regulado/compliance-profile-<nome>.json` declarado no projeto:
   - **registro** (vale para todos os comandos): impacto regulado e perfil registrados; perfil
     existente; impacto `sim` exige perfil. Sem registro, `kit` recusa (exit 1). Impacto `não`: o kit
     regulado não se aplica e `verificar` só confere o registro;
   - `verificar` (exit 1 com achado), com impacto `sim`: requisito sem teste · classe de risco fora
     da escala · risco alto sem mitigação ou teste · teste sem resultado · resultado sem evidência ·
     execução ou confirmação dos requisitos sem nome e data válida · norma revogada citada (padrões do
     perfil; linha que declara a revogação é permitida) · categoria de software fora do perfil ·
     sistema com categoria diferente do padrão do perfil sem registro datado de quem decidiu ·
     categoria de teste obrigatória do perfil ausente · referência a requisito ou teste inexistente ·
     tabela com número de colunas diferente do modelo · nenhum requisito, Parte F sem risco ou
     Parte G sem teste · requisito citado na Parte A sem linha de definição (formatos aceitos: `-`,
     `*`, `+`, numerado, negrito) ou definido duas vezes · campo de enquadramento duplicado;
   - `verificar --planejamento`: durante o projeto; aceita teste não executado e confirmação ainda
     não dada, e continua cobrando o resto. Liberação usa o modo estrito;
   - `matriz`: requisito → risco → teste → resultado → evidência, com a lacuna de cada linha;
   - `kit`: peças do kit comum do perfil + peças da categoria (só com impacto regulado).
3b. **Lista de neutralidade** (`tools/agnostic-denylist.txt`): atos normativos (RDC, IN) por sigla,
   só em maiúsculas (`(?-i:...)`, porque o linter roda sem distinguir caixa e "in 45/2020" é
   inglês), e por extenso ("Instrução Normativa", "Resolução da Diretoria Colegiada"), com amostra
   no `test_core_agnostic` (critério 5 do plano B3).
4. **Primeiro perfil:** `compliance-profile-farma-anvisa.json` (normas vigentes, 3 revogadas com
   substituta, peças por categoria 1/3/4/5, categoria padrão 4 para SAP — D2, testes obrigatórios).
   Fontes em `docs/specs/b3-documentacao-regulada/fontes.md`.
5. **Regra global, seções 7 e 8:** mapa de impacto em toda mudança (item B1.7 do plano do modo
   planejado); não existe perfil regulado padrão — o discovery pergunta impacto, órgão/perfil e
   empresa. `check_rules_parity`: 16 cláusulas.
6. **Nome do campo:** o plano B3 dizia "impacto em BPF". BPF é termo sanitário; com perfil por
   projeto (D1) o campo do motor é `Impacto regulado`, e a sigla fica no perfil. Registrado no
   Replanejamento do plano B3.

## Alternativas descartadas

- Regras sanitárias fixas no motor: viola ADR-020 e a D1 (ANP e outros ficariam sem uso).
- Planilha de rastreabilidade mantida à mão: diverge do texto; a matriz é gerada do `spec.md`.
- Arquivo separado para riscos e testes: contraria o ADR-117 (arquivo único sem perda).

## Régua §0

Reusa o leitor `spec_fonte`, o padrão de perfil do ADR-043 e a regra global. Adiciona 1 motor e
1 canário. Ganho: rastreabilidade e evidência passam de prosa a verificação executável, para
qualquer órgão, sem duplicar a lógica por perfil.

## Prova

- `tools/test_regulado.py`: especificação completa (3 requisitos, 2 riscos, 4 testes) passa; 32
  sabotagens reprovam com o achado esperado (8 delas vindas da rodada 1 do QA); 6 exceções
  legítimas passam (inclusive o modo `--planejamento`); perfil mínimo sem testes obrigatórios não
  deixa passar especificação vazia; matriz e kit conferidos com valores literais; `kit` recusa sem
  registro; motor sem termo da lista de neutralidade; perfis reais carregam; no perfil farma, a
  categoria 3 não traz especificação de configuração e a 4 traz (critério 1).
- Mutação do motor (script de sessão): 1ª versão, 18 mutações, 17 mortas (a viva expôs guarda
  redundante, removida); após a rodada 1 do QA, 32 mutações, 32 mortas.
- `tools/test_core_agnostic.py` PASS com os 5 padrões novos; caso [5b]: "in 45/2020", "released in
  3/2024", "in no case" e "rdc 5" em minúsculas não disparam.
- `tools/test_spec_unico.py` PASS e fotografia dos 4 gates nas 11 especificações antigas sem
  diferença (partes F e G não alteram as partes A–E).
- `tools/test_rules_parity.py`: 16 cláusulas, todas reprovadas quando apagadas.

## Limites

- Verifica forma e rastreabilidade, não a qualidade técnica do teste nem a veracidade da
  evidência (o caminho do arquivo não é aberto). Andaime de conformidade, não certificação.
- Código de documento controlado e modelo formal vêm da Qualidade da empresa (B3a-3).
- Planilhas no padrão real do MRP, ERU, relatório de validação e manifesto de evidência ficam nos
  incrementos B3a-2 e B3a-3 do plano B3.

## Estado do QA

| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado, primeiro plano (a88a6036673e80027) | FAIL | 1 CRÍTICA: requisito com `*` sumia e, sem teste, passava. 1 ALTA: Parte F vazia passava. 2 MÉDIA: "Instrução Normativa" por extenso não casava; "in 45/2020" (inglês) casava. 2 BAIXA: campo duplicado não acusado; perfil sem testes obrigatórios deixaria especificação vazia passar | definição de requisito aceita `-`, `*`, `+`, numerado e negrito, e toda outra menção sem definição é acusada; exigidos ≥ 1 requisito, risco e teste; siglas só em maiúsculas e formas por extenso na lista; campo duplicado e requisito duplicado acusados; 8 casos novos no canário |
