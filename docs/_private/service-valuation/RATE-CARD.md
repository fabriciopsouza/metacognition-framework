# RATE-CARD.md — configuração de mercado

Arquivo de **configuração** da skill `service-valuation`. O método está na skill; os números
estão aqui. Alterar sempre aqui, nunca na skill.

- Moeda: BRL. Base: mercado brasileiro. Revisão: a cada 6 meses.
- Última revisão: preencher na primeira execução.
- Classificação global deste arquivo: `[INFERIDO / confiança MÉDIA]`, exceto linhas marcadas
  como `[CONFIRMADO]` por contrato ou proposta real anexada.
- **Regra de precedência**: `HISTORICO-ENTREGAS.md` > contrato vigente > proposta recebida >
  este arquivo.

---

## 1. Taxas por perfil e disciplina

| ID | Disciplina | Perfil | Mín | Provável | Máx |
|---|---|---|---|---|---|
| T-01 | ERP funcional | Consultor pleno | 170 | 220 | 300 |
| T-02 | ERP funcional | Consultor sênior | 230 | 300 | 420 |
| T-03 | ERP funcional | Especialista / arquiteto | 330 | 450 | 650 |
| T-04 | ERP técnico | Desenvolvedor pleno | 140 | 190 | 260 |
| T-05 | ERP técnico | Desenvolvedor sênior | 190 | 260 | 350 |
| T-06 | Analytics/BI | Analista pleno (Power BI, Tableau, SAC) | 130 | 180 | 250 |
| T-07 | Analytics/BI | Especialista sênior / modelagem semântica | 200 | 270 | 380 |
| T-08 | Analytics/BI | Arquiteto de analytics | 280 | 380 | 520 |
| T-09 | Engenharia de dados | Engenheiro pleno (Python, SQL, ETL) | 150 | 200 | 280 |
| T-10 | Engenharia de dados | Engenheiro sênior / arquiteto de dados | 230 | 310 | 430 |
| T-11 | Automação/RPA | Desenvolvedor de automação (Power Automate, scripts) | 130 | 180 | 250 |
| T-12 | Automação/RPA | Especialista sênior / arquiteto de automação | 200 | 270 | 380 |
| T-13 | Integração/API | Especialista de integração | 200 | 280 | 400 |
| T-14 | IA/ML/LLM | Cientista de dados / engenheiro de ML | 200 | 290 | 420 |
| T-15 | IA/ML/LLM | Especialista sênior em IA aplicada | 300 | 420 | 600 |
| T-16 | Cloud/infra | Engenheiro cloud | 180 | 250 | 350 |
| T-17 | Qualidade e validação | Especialista CSV / GxP | 270 | 360 | 500 |
| T-18 | Qualidade e validação | QA / teste | 130 | 180 | 250 |
| T-19 | Gestão/PMO | Gerente de projeto | 320 | 430 | 600 |
| T-20 | Treinamento | Instrutor técnico (hora de aula) | 200 | 320 | 500 |
| T-21 | Consultoria de processo | Consultor de negócio sênior | 250 | 350 | 500 |
| T-22 | Multidisciplinar | AMS por chamado, blended | 150 | 210 | 300 |

Notas de leitura: **pleno** entrega com supervisão pontual; **sênior** entrega sozinho e
responde pela solução; **especialista/arquiteto** decide desenho e responde por impacto
sistêmico. Instrutor é hora de aula, não hora de preparo, que entra como `F-04`.

## 2. Derivação usada nas faixas acima

```
custo_hora_interno = salário_mensal × (1 + 0,75) ÷ 168
taxa_faturada      = custo_hora_interno × markup
```

| Modelo de contratação | Markup |
|---|---|
| Body shop / alocação | 2,0x a 2,5x |
| Projeto com escopo fechado | 2,5x a 3,0x |
| Consultoria de marca global | 3,5x ou mais |
| AMS em escala | 1,8x a 2,2x |

## 3. Ajuste por modelo de suporte

Multiplicadores sobre a taxa da tabela 1, quando o modelo diferir do default de projeto:

| Modelo | Ajuste |
|---|---|
| AMS por chamado | 0,70 a 0,85 |
| Bolsa de horas com compromisso de volume | 0,80 a 0,90 |
| Body shop de longa duração | 0,85 a 0,95 |
| Projeto com escopo fechado | 1,00 |
| Consultoria pontual / diagnóstico curto | 1,20 a 1,50 |
| Plantão, on-call ou fora do horário | 1,50 a 2,00 |

## 4. Unidades de entrega por disciplina

Faixas de esforço típico por unidade, para a lente de mercado comparável.
**Todas `[INFERIDO / confiança BAIXA]`.** Servem como sanidade, não como preço. Substituir
pelo histórico próprio assim que houver três entregas do mesmo tipo.

| Disciplina | Unidade | Simples | Médio | Complexo |
|---|---|---|---|---|
| ERP técnico | objeto (relatório, enhancement, interface) | 8 a 20 h | 20 a 60 h | 60 a 200 h |
| ERP funcional | processo parametrizado ponta a ponta | 40 a 80 h | 80 a 200 h | 200 a 600 h |
| Analytics/BI | dashboard publicado, fonte pronta | 16 a 40 h | 40 a 100 h | 100 a 250 h |
| Analytics/BI | modelo semântico corporativo | 60 a 120 h | 120 a 300 h | 300 a 800 h |
| Engenharia de dados | pipeline de ingestão por fonte | 24 a 60 h | 60 a 160 h | 160 a 400 h |
| Automação/RPA | fluxo de processo automatizado | 16 a 40 h | 40 a 120 h | 120 a 300 h |
| Integração/API | integração ponto a ponto | 40 a 80 h | 80 a 200 h | 200 a 500 h |
| IA/ML/LLM | caso de uso em produção | 80 a 160 h | 160 a 400 h | 400 a 1.200 h |
| Consultoria de processo | processo mapeado com RACI e gaps | 24 a 60 h | 60 a 160 h | 160 a 400 h |
| Treinamento | turma de 8 h, material novo | 24 a 40 h | 40 a 80 h | 80 a 160 h |

Critério de complexidade: **simples** = uma fonte, uma regra, sem integração;
**médio** = múltiplas fontes ou regras, um ambiente de homologação;
**complexo** = múltiplos sistemas, ambiente regulado, ou impacto em obrigação legal.

## 4.1 Preço de resultado equivalente — a alternativa do cliente

A Lente B compara **resultado**, e não só hora. Sem pelo menos uma linha aqui, a Lente B fica
`[DESCONHECIDO]` (regra 9 da skill). Preencher com cotação real sempre que houver.

| ID | Alternativa | Faixa | Fonte | Classificação |
|---|---|---|---|---|
| M-01 | Integrador de RPA — automação de processo com conector de ERP, escopo fechado | preencher | | `[DESCONHECIDO]` |
| M-02 | Plataforma de automação com licença (UiPath, Power Automate, Automation Anywhere) — implantação de 1 fluxo | preencher | | `[DESCONHECIDO]` |
| M-03 | Módulo de mercado que resolve o mesmo problema (self-service de senha, IAM) | preencher | | `[DESCONHECIDO]` |
| M-04 | Não fazer: manter o processo manual | custo do processo hoje | | `[DESCONHECIDO]` |

**Uma cotação real aqui vale mais que toda a seção 1.** Ela é `[CONFIRMADO]` e vence o rate
card por precedência.

## 5. Custo-hora interno do cliente

Usado no componente `V-02` (ganho operacional recorrente). Preencher com a realidade do
cliente. Sem isso, `V-02` fica `[DESCONHECIDO]`, não zero.

| Perfil do cliente | Custo-hora interno |
|---|---|
| Operador / auxiliar administrativo | preencher |
| Analista | preencher |
| Coordenador / especialista | preencher |
| Gerente | preencher |

Fórmula: `salário_mensal × (1 + encargos) ÷ 168`.

## 6. Premissas globais editáveis

| ID | Premissa | Default |
|---|---|---|
| P-G1 | Encargos sobre salário CLT | 75% |
| P-G2 | Horas úteis por mês | 168 |
| P-G3 | Contingência sobre esforço | 15% |
| P-G4 | Despesas com deslocamento | 8% presencial, 0% remoto |
| P-G5 | Taxa de captura de valor | 5% a 15% do benefício do 1º ano |
| P-G6 | Horizonte do benefício no cálculo do teto | 12 meses, sem perpetuidade |

## 7. Registro de calibração

Toda vez que uma entrega real fechar, registrar aqui e em `HISTORICO-ENTREGAS.md`.

| Data | Disciplina | Unidade | Horas estimadas | Horas reais | Desvio | Preço praticado |
|---|---|---|---|---|---|---|
| | | | | | | |

Três linhas na mesma disciplina e unidade autorizam substituir a faixa da tabela 4 por média
própria, e a classificação da linha sobe de `[INFERIDO / BAIXA]` para `[CONFIRMADO / MÉDIA]`.
