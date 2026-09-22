# Memória de cálculo — valoração de serviço

| Campo | Conteúdo |
|---|---|
| Serviço / chamado | |
| Cliente / área | |
| Período de execução | |
| Autor da valoração | |
| Data | |
| Versão | 1.0 |
| Existe proposta comercial de referência? | Sim / Não |

> Legenda de classificação, aplicada a toda linha numérica:
> origem `[CONFIRMADO]` `[INFERIDO]` `[DESCONHECIDO]` · confiança `[ALTA]` `[MÉDIA]` `[BAIXA]`

---

## 1. Classificação da demanda

| Eixo | Escolha | Justificativa (uma frase) | ID |
|---|---|---|---|
| Natureza | | | P-01 |
| Tipo de suporte necessário | | | P-02 |
| Criticidade | | | P-03 |
| Ambiente | | | P-04 |
| Escassez do conhecimento | | | P-05 |
| Reversibilidade | | | P-06 |
| Recorrência do benefício | | | P-07 |

## 2. Evidência do trabalho

| ID | Item | Origem literal (caminho, commit, chamado, data) | Classificação |
|---|---|---|---|
| E-01 | | | `[CONFIRMADO / ALTA]` |
| E-02 | | | |

## 3. Esforço reconstruído

| ID | Fase | Perfil | h mín | h prov | h máx | Evidência | Classificação |
|---|---|---|---|---|---|---|---|
| F-01 | Entendimento e diagnóstico | | | | | E-01 | `[INFERIDO / MÉDIA]` |
| F-03 | Especificação | | | | | | |
| F-04 | Construção | | | | | | |
| F-05 | Teste unitário | | | | | | |
| F-08 | Documentação | | | | | | |
| F-09 | Homologação | | | | | | |
| F-10 | Transporte e produção | | | | | | |
| F-12 | Gestão | | | | | | |
| | **Total** | | | | | | |

Fases omitidas e por quê:

## 4. Taxas aplicadas

| ID | Perfil | R$/h usado | Origem | Classificação |
|---|---|---|---|---|
| T-01 | | | contrato / proposta / rate card / derivação | |

Derivação, quando aplicável:
`custo_hora = salário × (1 + encargos) ÷ 168` · `taxa = custo_hora × markup`

## 5. Lente A — Custo (piso)

| ID | Item | Mín | Provável | Máx |
|---|---|---|---|---|
| C-01 | Custo base (Σ horas × taxa) | | | |
| C-02 | Contingência (P-08 = __%) | | | |
| C-03 | Despesas (P-09 = __%) | | | |
| C-04 | **Piso = C-01 + C-02 + C-03** | | | |

## 6. Lente B — Mercado comparável (referência)

| ID | Comparável | Valor | Fonte | Classificação |
|---|---|---|---|---|
| C-05 | | | | |

Multiplicadores aplicados:

| ID | Fator | Valor | Justificativa |
|---|---|---|---|
| P-10 | | | |

`C-06 = Referência ajustada`

## 7. Lente C — Valor entregue (teto)

| ID | Componente | Valor anual | Como foi calculado | Classificação |
|---|---|---|---|---|
| V-01 | Custo evitado | | | |
| V-02 | Ganho operacional recorrente | | | |
| V-03 | Receita destravada | | | |
| V-04 | Custo de reposição | | | |
| V-05 | Risco transferido | | | |
| V-06 | Valor de opção | | | |
| C-07 | **Valor anual total** | | | |
| C-08 | **Teto = C-07 × captura (P-11 = __%)** | | | |

Componentes marcados `[DESCONHECIDO]` e o dado que falta para fechá-los:

## 8. Triangulação e resultado

| Lente | Valor |
|---|---|
| Piso (C-04) | |
| Referência (C-06) | |
| Teto (C-08) | |
| **Preço provável** | |
| **Faixa recomendada** | |

Lente que domina o resultado e por quê:

Conduta conforme o caso (Teto > Referência > Piso · Teto entre Piso e Referência · Teto < Piso):

## 9. Revisão adversarial

| # | Verificação | Resultado |
|---|---|---|
| 1 | Fase cobrada sem evidência | |
| 2 | Diagnóstico entregue pronto e cobrado cheio | |
| 3 | Escopo cobre todos os cenários da evidência | |
| 4 | Fase com zero horas que vai acontecer | |
| 5 | Benefício contado em duplicidade | |
| 6 | Multiplicador aplicado duas vezes | |
| 7 | Taxa coerente com o modelo de suporte | |
| 8 | Recorrência anualizada sem perpetuidade | |
| 9 | `[INFERIDO]` apresentado como `[CONFIRMADO]` | |
| 10 | Terceiro consegue refazer a conta sozinho | |

Furos encontrados e como foram tratados:

## 10. Riscos e perguntas em aberto

| ID | Risco / pergunta | Impacto no preço | A quem perguntar |
|---|---|---|---|
| R-01 | | | |

## 11. Conclusão (máximo cinco linhas)

- Preço provável:
- Faixa:
- Lente dominante:
- Maior risco:
- Próxima decisão:
