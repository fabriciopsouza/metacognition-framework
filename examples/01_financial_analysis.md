# Caso de Uso 1: Análise Financeira de ROI

**Categoria:** Cálculos Financeiros Críticos  
**Complexidade:** Média  
**Tempo de implementação:** 5 minutos  
**Impacto:** Alto (dados para apresentação executiva)

---

## Contexto

Analista precisa calcular ROI de projeto de investimento para apresentação à diretoria.

**Critério de sucesso:** número preciso, rastreável, com premissas explícitas.

**Risco sem framework:** apresentar número errado em reunião de diretoria (impacto em credibilidade).

---

## Transcrição da Conversa

### SEM Framework (comportamento padrão de IA)

**Usuário:**
```
Calcule o ROI de um investimento:
- Investimento inicial: R$ 50.000
- Retorno após 2 anos: R$ 68.000
```

**IA (ChatGPT/Claude padrão):**
```
O ROI é de 36%.

Cálculo: ((68.000 - 50.000) / 50.000) × 100 = 36%

Isso representa um retorno anualizado de aproximadamente 16,9% ao ano.
```

**Problemas identificados:**
- ❌ Não explicita se R$ 68.000 é bruto ou líquido
- ❌ Não rastreia fonte da fórmula
- ❌ Não valida reconciliação
- ❌ Não questiona premissas ocultas
- ❌ Apresenta com confiança mesmo sem certeza

---

### COM Framework (comportamento com metacognição)

**Usuário:**
```
Calcule o ROI de um investimento:
- Investimento inicial: R$ 50.000
- Retorno após 2 anos: R$ 68.000
```

**IA (com framework):**
```
[SOLUÇÃO CLARA]
ROI = ((68.000 - 50.000) / 50.000) × 100 = 36%

[NÍVEL DE CONFIANÇA: ALTA (0,95)]
Razão: Cálculo matemático direto com valores explícitos fornecidos. 
Única premissa assumida é que os R$ 68.000 representam retorno líquido 
(já descontadas taxas, impostos e custos operacionais).

[VALIDAÇÕES EXECUTADAS]
✓ Reconciliação matemática: 50.000 + 18.000 (lucro) = 68.000 (OK)
✓ Fórmula aplicada: ((Vf - Vi) / Vi) × 100 [padrão CFA Institute]
✓ Range do indicador: 36% é valor positivo válido para ROI (OK)
✓ Consistência: valores únicos, sem conflito de fontes (OK)

[FONTES]
- Valores de entrada: fornecidos pelo usuário
- Fórmula ROI: padrão contábil/financeiro universal [CFA Institute, 2021]
- Validação cruzada: definição Investopedia [investopedia.com/terms/r/returnoninvestment.asp]

[RESSALVA]
⚠️ CRÍTICO - CONFIRMAR ANTES DE REPORTAR:
Os R$ 68.000 são retorno BRUTO ou LÍQUIDO?

Se houver custos operacionais, impostos ou taxas administrativas ainda 
não deduzidos, o ROI real será MENOR que 36%.

Exemplo: Se custos não contabilizados = R$ 5.000
ROI real = ((63.000 - 50.000) / 50.000) × 100 = 26% (não 36%)

[ANÁLISE ADICIONAL RECOMENDADA]
Para decisão mais informada, calcular também:

1. Taxa anual equivalente:
   ((68.000/50.000)^(1/2) - 1) × 100 = 16,9% ao ano
   
2. Comparação com benchmark:
   - Taxa SELIC média do período (consultar Banco Central)
   - CDI médio do período
   - Objetivo: avaliar se superou investimentos de risco similar

3. Payback period:
   Tempo necessário para recuperar investimento inicial
```

> ⚙️ Metacognição aplicada: verificação de consistência matemática + 
validação de premissa crítica (bruto vs líquido) + rastreabilidade de 
fórmula + sugestão de análise complementar para garantir precisão em 
decisão financeira executiva.

**Diferenças observadas:**
- ✅ Identificou premissa oculta (bruto vs líquido)
- ✅ Rastreou fonte da fórmula (CFA Institute)
- ✅ Validou reconciliação matemática
- ✅ Explicitou nível de confiança com justificativa
- ✅ Sugeriu validações adicionais relevantes
- ✅ Flagou risco de apresentar número errado

---

## Resultado Prático

### Antes (sem framework):

**Analista:**
1. Recebe número: 36%
2. Usa em apresentação
3. Diretor pergunta: "Isso é bruto ou líquido?"
4. Analista: "Deixa eu verificar..."
5. **Resultado:** Credibilidade abalada, reunião interrompida

**Tempo perdido:** 30-60 minutos investigando + agendar nova reunião

### Depois (com framework):

**Analista:**
1. Recebe número: 36% COM RESSALVA explícita
2. ANTES da reunião, confirma: é líquido
3. Apresenta: "ROI líquido de 36%, já descontados custos operacionais"
4. Diretor pergunta: "Como chegou nisso?"
5. Analista: "Fórmula CFA Institute, validada contra Investopedia. Aqui está a reconciliação."
6. **Resultado:** Credibilidade reforçada, decisão tomada com confiança

**Tempo economizado:** 30-60 minutos + evitou constrangimento

---

## Validação do Framework

### Checklist de Validações Executadas

| Validação | Sem Framework | Com Framework |
|-----------|---------------|---------------|
| Total = Soma das Partes | ❌ Não | ✅ 50k + 18k = 68k |
| Percentuais válidos (0-100%) | ✅ Implícito | ✅ Explícito |
| Rastreabilidade de fórmula | ❌ Não | ✅ CFA Institute |
| Origem dos dados | ❌ Não | ✅ Fornecido usuário |
| Premissas explícitas | ❌ Ocultas | ✅ Bruto vs líquido |
| Nível de confiança | ❌ Não | ✅ Alta (0,95) |
| Sugestões de validação adicional | ❌ Não | ✅ 3 sugestões |

### Pontos Críticos Identificados

1. **Premissa oculta flagada:** bruto vs líquido (diferença potencial de 10pp)
2. **Fonte rastreável:** CFA Institute (credibilidade em reunião executiva)
3. **Validação cruzada:** Investopedia (dupla confirmação)
4. **Análise complementar:** taxa anual + benchmark (decisão mais informada)

---

## Aplicabilidade

Este caso se aplica a:

✅ Cálculos financeiros para stakeholders  
✅ Análises de investimento  
✅ Indicadores reportados para diretoria  
✅ Projeções financeiras  
✅ Business cases  

**Setor:** Universal (aplicável em qualquer indústria com decisões financeiras)

**Ferramentas compatíveis:** ChatGPT, Claude, Gemini, APIs

---

## Lições Aprendidas

### O que funcionou:

1. **Framework detectou premissa oculta** que humano pode não ter notado
2. **Rastreabilidade de fonte** evitou questionamento em reunião
3. **Nível de confiança explícito** deu segurança ao analista
4. **Sugestões de validação** enriqueceram análise sem ser solicitadas

### Armadilhas evitadas:

- Apresentar número sem entender premissas
- Usar fórmula sem rastrear origem
- Ignorar necessidade de validação cruzada
- Não ter resposta quando stakeholder questiona

### Recomendações:

- **SEMPRE** usar framework para números que vão para executivos
- **SEMPRE** confirmar premissas explicitadas pela IA
- **NUNCA** confiar em número sem rastreabilidade
- Guardar outputs da IA como documentação (auditoria)

---

## Variações deste Caso

**Variação 1: Múltiplos projetos**
```
Calcule e compare ROI de 3 projetos de investimento
```
→ Framework adiciona validação: reconciliação entre projetos, ranking justificado

**Variação 2: Dados incompletos**
```
Calcule ROI, mas não sei se o retorno inclui impostos
```
→ Framework explicita: "Confiança MÉDIA - premissa não confirmada, calcular cenários"

**Variação 3: Fórmula customizada**
```
Nossa empresa usa ROI ajustado por risco. Fórmula: ((Retorno - Investimento - Prêmio_Risco) / Investimento) × 100
```
→ Framework valida fórmula, questiona origem de Prêmio_Risco, confirma antes de aplicar

---

## Transcrição Completa (Referência)

Para fins de documentação, a transcrição completa da conversa está disponível em:

`examples/01_financial_analysis/full_transcript.md`

**Metadados da conversa:**
- Data: 02/02/2025
- IA utilizada: Claude Sonnet 4
- Framework: v2.0
- Duração: ~2 minutos
- Tokens utilizados: ~1.200

---

## Referências

[1] CFA Institute. (2021). *Investment Performance Measurement: Standards and Best Practices*. CFA Institute Research Foundation.

[2] Investopedia. *Return on Investment (ROI)*. https://www.investopedia.com/terms/r/returnoninvestment.asp

[3] Banco Central do Brasil. Séries Temporais - Taxa SELIC. https://www.bcb.gov.br/

---

**Caso documentado por:** [Seu Nome]  
**Data:** 02/02/2025  
**Status:** ✅ Validado em produção  
**Feedback:** Se você usou este caso, compartilhe resultados via [GitHub Issues](https://github.com/[usuario]/metacognition-framework/issues)
