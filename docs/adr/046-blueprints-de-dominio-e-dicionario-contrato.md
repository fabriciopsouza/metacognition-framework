# ADR 046 — Blueprints de produto por domínio + dicionário-contrato de entrada + ux-gate premium

- Status: Aceito
- Data: 2026-06-01 · Decisores: dono + squad (architect)
- Tipo: **EMENDA/extensão** ao ADR-023 (apps SW/dados) — net-gain por destravar **assertividade** (menos interações) e mecanizar validação de entrada (verificação inalcançável hoje). Carregado sob demanda (não infla o núcleo).
- Origem: feedback de campo do dono — o produto entregue pelo framework saía sub-premium (GUI básica, difícil para leigo, sem validação de arquivos) e exigia ~12 interações; um produto de referência (vibe-coded) chegou a launcher premium + suíte de relatórios + dicionário de dados. Relaciona: ADR-022 (product_type), ADR-033 (dimensões), ADR-036 (porta do usuário), ADR-034/038 (completude/report).

## Contexto

O framework garantia **cobertura** (a dimensão `interface` foi endereçada?) mas **não tinha memória de
"como é um entregável premium"** por domínio. Resultado: o discovery elicitava aos pedaços (o dono virava
professor — ~12 interações) e a GUI passava por *existir*, não por ser usável/validada. As dores
concretas: GUI não-premium, difícil para leigo, **sem validação/auto-detecção de arquivos**, abas confusas.

## Decisão (1 frase ativa)

Adicionar **blueprints de produto por domínio** (`exemplos/dominio-software|processo|projeto/blueprint.md`,
carregados **sob demanda** pelo discovery quando o `product_type` casa) que fazem o discovery **PROPOR a
forma premium completa de uma batelada** (launcher fácil-ou-CLI · suíte de saída · auditoria), um
**dicionário-contrato de entrada** (`docs/specs/_template/data-dictionary.md` + `tools/check_input_contract.py`
+ canário) que **auto-detecta e valida** os arquivos na pasta, e um **ux-gate premium** (checklist de
"pronto" no `ux-designer`) — tudo **agnóstico** (forma, não conteúdo) e fora do núcleo (P12 preservado).

## Alternativas consideradas (≥3)

1. **Manter só cobertura (status quo).** Discovery elicita aos pedaços; GUI sub-premium passa. **Rejeitada — é o gap.**
2. **Hardcodar a forma premium no núcleo (ou um "gerador de GUI").** Viola P12 (domínio/forma de produto no núcleo) e infla. **Rejeitada** — blueprints vivem em `exemplos/`, carregados sob demanda.
3. **Avaliar "qualidade estética" da GUI mecanicamente.** Não-determinístico; beleza é julgamento. **Rejeitada** — o ux-gate verifica **estrutura premium** (launcher/leigo/validação/estados), não beleza.
4. **Blueprints sob demanda + dicionário-contrato + ux-gate (ESCOLHIDA).** Prós: assertividade (propor, não perguntar) → menos interações; auto-detecção+validação de arquivos mecanizada; núcleo agnóstico e não-inflado (progressive disclosure). Contras: "premium de verdade" segue parcialmente julgamento — limite declarado em LIMITS.md.

## Consequências

**Positivas:** o discovery propõe o produto premium de uma vez (menos round-trips); "produto sem validação
de arquivos" vira FAIL mecânico (`check_input_contract`); GUI sub-premium é barrada pelo ux-gate; 3 domínios
(software/processo/projeto) viram aplicações irmãs, extensíveis via `_template` sem tocar o núcleo.
**Negativas:** +3 pastas em `exemplos/` (fora do núcleo) — aceitável (não inflam contexto; carregam sob
demanda). **Riscos/limite declarado:** o gate prova **presença/estrutura** (launcher, dicionário, suíte),
**não estética premium** nem **mapeamento semântico correto** (este último = qa-critic/dicionário) → LIMITS.md.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.33-blueprints` · `2026-06-01` · grep `check_input_contract|blueprint|data-dictionary`
- Artefatos: `tools/check_input_contract.py` + `tools/test_input_contract.py`; `docs/specs/_template/data-dictionary.md`;
  `exemplos/dominio-software/blueprint.md` + `exemplos/dominio-processo/` + `exemplos/dominio-projeto/`
  (blueprint.md + product-types.txt); edição `ux-designer/SKILL.md` (§Definição de pronto premium) e
  `discovery/SKILL.md` (§Blueprint de domínio). Claim no `build_limits` (ADR-044) + canário no CI.
- Housekeeping junto: terminologia **"genérico" → "flexível"** nos docs/papéis voltados ao usuário
  (mantendo "agnóstico", termo técnico preciso) — "genérico soa mal" (pedido do dono).
- DONE quando: canário verde no CI + blueprints sob demanda + dicionário-contrato validando arquivos.
