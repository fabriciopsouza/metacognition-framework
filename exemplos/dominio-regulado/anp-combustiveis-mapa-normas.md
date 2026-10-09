# Perfil anp-combustiveis — mapa peça → norma

- **Escopo:** sistemas que registram ou informam movimentação, estoque, medição e qualidade na **distribuição** de combustíveis líquidos (Brasil). Perfil de aplicação: não cita empresa.
- **Perfil:** `compliance-profile-anp-combustiveis.json`, na mesma pasta.
- **Pesquisa:** 28/09/2026. Fontes (URL, data de acesso), vigência e pendências: `C:\Users\fabriciosouza\metacognition-framework\docs\specs\perfil-anp\fontes.md`.
- **Achado que molda o perfil:** a ANP não exige do distribuidor validação de sistema computadorizado, integridade de dados nem trilha de auditoria. A busca nos textos oficiais e nos manuais do i-SIMP foi negativa. O perfil só pede o que a norma exige.
- **Marcas:**
  - **CONFIRMADO:** trecho lido no texto oficial;
  - **INFERIDO:** fonte secundária, ementa sem o artigo lido, ou texto oficial lido de cópia sem URL de origem
    registrada (Res. 807/2020 e 898/2022; reconferir no in.gov.br);
  - **DESCONHECIDO:** não achado;
  - **NÃO SE APLICA:** peça de gestão do projeto ou forma do framework.
- **Regra de manutenção:** toda peça do perfil tem pelo menos uma linha aqui, com a coluna Peça escrita igual ao perfil. Quem confere é `python tools/regulado.py mapa <perfil.json>`, rodado pelo canário `test_regulado`.

## Peças de gestão do projeto (kit comum)

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `TAP` | — | — | peça de gestão do projeto | NÃO SE APLICA |
| `especificacao` | — | — | arquivo único do projeto | NÃO SE APLICA |
| `HANDOFF` | — | — | peça de gestão do projeto | NÃO SE APLICA |
| `glossario` | — | — | peça de gestão do projeto | NÃO SE APLICA |
| `cronograma` | — | — | peça de gestão do projeto | NÃO SE APLICA |

## Movimentação, estoque e medição

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `registro-de-movimentacao-e-estoque` | Res. ANP 950/2023 | art. 22, IX e parágrafo único | "pelo prazo de seis meses, todos os registros de movimentação e estoques de combustíveis líquidos escriturados e atualizados, bem como as notas fiscais de aquisição e de venda" · período anterior: apresentar "no prazo de dez dias" | CONFIRMADO |
| `correcao-a-20c` | Res. ANP 894/2022 | art. 1º e parágrafo único | "estabelece, para uso na comercialização dos derivados do petróleo, o coeficiente de correção para temperatura de 20°C, da densidade (massa específica) e do volume" (Tabelas I e II publicadas no site da ANP) | CONFIRMADO |
| `volume-na-nota-fiscal` | Convênio ICMS 110/07 | cláusula nona, § 8º | volume "convertido a 20º C, quando emitida pelo produtor nacional [...]" e "à temperatura ambiente, quando emitida pelo distribuidor de combustíveis ou pelo TRR" | CONFIRMADO |
| `volume-na-nota-fiscal` | NT NF-e 2023.001 | campo LA05 `qTemp` | "Quantidade de combustível faturada à temperatura ambiente" | CONFIRMADO |
| `perdas-e-sobras` | Manual i-SIMP Distribuidores v1.3 (06/04/2020) | códigos 1021001 e 1022004 | "SOBRAS DE PROCESSO" e "PERDAS DE PROCESSO", quantidades "considerando à temperatura de 20° Celsius e pressão de 1 (uma) atmosfera"; sem limite de tolerância para o distribuidor | CONFIRMADO |
| `calibracao-de-medicao` | Portaria INMETRO 227/2022 | itens 3.1.1 e 3.1.2 | "Os erros máximos admissíveis de ±0,3% devem ser aplicados [...] na verificação inicial"; "±0,5%" nas verificações subsequentes | CONFIRMADO |
| `calibracao-de-medicao` | Portaria INMETRO 49/2022 | itens 2.2.1, 2.2.2 e 5.3.4 | veículo-tanque: volumes "referidos à temperatura de 20 °C"; "erro máximo admissível [...] 0,25 %"; verificação com "validade de 2 (dois) anos" | CONFIRMADO |
| `calibracao-de-medicao` | Portaria INMETRO 291/2021 | ementa (artigo não lido) | RTM de "sistemas de medição dinâmica para medição de quantidades de líquidos"; revogou a Portaria 64/2003 | INFERIDO |
| `calibracao-de-medicao` | Portaria INMETRO 103/2022 | ementa (artigo não lido) | arqueação de tanque fixo, conforme a lista da página oficial do INMETRO atualizada em 09/09/2026 | INFERIDO |

## Envio de dados à ANP

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `envio-isimp` | Res. ANP 950/2023 | art. 23, caput e § 2º | "deverá enviar, até o dia quinze e cada mês, a informação sobre sua comercialização de combustíveis líquidos, referente ao mês anterior, por meio do aplicativo do I-Simp" (o "e" em "dia quinze e cada mês" é erro do próprio DOU) · 2 meses consecutivos sem envio levam à interdição | CONFIRMADO |
| `envio-isimp` | Res. ANP 729/2018 | art. 2º, caput e § 6º | "devem ser enviadas mensalmente à ANP, até o dia quinze do mês subsequente" · "mesmo que não tenha ocorrido movimentação" | CONFIRMADO |
| `reprocessamento-isimp` | Res. ANP 729/2018 | art. 2º, §§ 4º e 5º | "O reprocessamento dos dados [...] estando sujeito à aprovação prévia da Agência." · "O arquivo de reprocessamento tem a mesma natureza do originalmente apresentado, substituindo-o integralmente." | CONFIRMADO |
| `estoque-diario` | Res. ANP 868/2022 | arts. 3º e 4º | "em todos os dias úteis, por meio do sistema de processamento de arquivos da ANP - IEngine" · "até às 12 horas (horário de Brasília) do dia útil seguinte ao fechamento do estoque" | CONFIRMADO |
| `estoque-minimo` | Res. ANP 949/2023 | art. 2º, II; art. 6º | "EmínimoD = KD (CD/30)" · "devem assegurar estoques semanais médios (EsmD) [...] iguais ou superiores ao estoque mínimo requerido" | CONFIRMADO |

## Qualidade

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `boletim-de-conformidade` | Res. ANP 807/2020 | arts. 9º e 10 | "O distribuidor de combustíveis líquidos deverá analisar uma amostra representativa do volume de gasolina C a ser comercializado [...] e emitir o boletim de conformidade." · guarda "pelo prazo de doze meses" | INFERIDO |
| `boletim-de-conformidade` | Res. ANP 828/2020 | art. 5º, § 1º; art. 40, II | conteúdo do boletim; "à disposição da ANP pelo prazo de doze meses" | CONFIRMADO |
| `certificado-no-recebimento` | Res. ANP 950/2023 | art. 22, V | "solicitar ao fornecedor autorizado o certificado de qualidade do combustível, conforme o caso, no ato de seu recebimento" | CONFIRMADO |
| `recusa-fora-de-especificacao` | Res. ANP 907/2022 | art. 8º | distribuidor "obrigados a recusar o recebimento [...] caso constate qualquer não-conformidade" | CONFIRMADO |
| `rastreabilidade-na-nota-fiscal` | Res. ANP 807/2020 | art. 11, I e II | o documento fiscal traz "o código e a descrição do produto estabelecidos pela ANP" e "o número do boletim de conformidade" | INFERIDO |
| `rastreabilidade-na-nota-fiscal` | Res. ANP 898/2022 | art. 7º, § 3º | "O número do envelope de segurança da amostra-testemunha deverá ser indicado, em campo apropriado, na documentação fiscal" | INFERIDO |
| `lacre-e-amostra-testemunha` | Res. ANP 898/2022 | art. 2º e § 1º; art. 7º, § 1º | compartimentos, bocais e válvulas "lacrados"; o lacre é obrigação de quem vende ao posto · "O envelope de segurança e o frasco para coleta deverão ser fornecidos pelo distribuidor de combustíveis líquidos." | INFERIDO |

## Documento emitido e itens do checklist

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `checklist-de-prontidao` | — | — | forma do framework para a liberação; cada item tem base abaixo | NÃO SE APLICA |
| `Envio ao i-SIMP até o dia 15` | Res. ANP 950/2023 | art. 23 | mesma base da peça `envio-isimp` | CONFIRMADO |
| `Estoque diário até as 12 h do dia útil seguinte` | Res. ANP 868/2022 | art. 4º | mesma base da peça `estoque-diario` | CONFIRMADO |
| `Registros disponíveis por 6 meses` | Res. ANP 950/2023 | art. 22, IX | mesma base da peça `registro-de-movimentacao-e-estoque` | CONFIRMADO |
| `Correção a 20 °C pelas tabelas da ANP` | Res. ANP 894/2022 | art. 1º, parágrafo único | Tabelas I e II no site da ANP | CONFIRMADO |
| `Instrumentos de medição com verificação vigente` | Portaria INMETRO 49/2022 | item 5.3.4 | verificação do veículo-tanque com "validade de 2 (dois) anos" | CONFIRMADO |

## Testes obrigatórios com impacto

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `integridade de registros` | Lei 9.847/1999 | art. 3º, V | multa para quem "prestar declarações ou informações inverídicas, falsificar, adulterar, inutilizar, simular ou alterar registros e escrituração" | CONFIRMADO |
| `retenção de registros` | Res. ANP 950/2023 | art. 22, IX | "pelo prazo de seis meses, todos os registros de movimentação e estoques" | CONFIRMADO |

## O que a norma não traz (não citar como exigência)

- **Validação de sistema, trilha de auditoria e assinatura eletrônica:** não há exigência ao distribuidor.
- **Tolerância de perda para a distribuidora:** não achada, nem na ANP nem no ICMS.
  - Os 0,6% são do posto: a Res. ANP 884/2022, art. 5º, usa o valor como gatilho de investigação no livro de movimentação de combustíveis (LMC).
  - Tolerância própria da empresa entra pela camada privada.
- **Guarda por 5 anos:** vale para o TRR e para a legislação fiscal. Para o distribuidor, a ANP exige 6 meses.
- **Resolução Conjunta ANP/INMETRO 1/2013:** não se aplica a derivados líquidos (item 1.2.3.2). A base da correção a 20 °C é a Res. ANP 894/2022.
