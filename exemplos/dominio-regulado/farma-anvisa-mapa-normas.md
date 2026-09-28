# Perfil farma-anvisa — mapa peça → norma

- **Escopo:** sistemas computadorizados com impacto em Boas Práticas de Fabricação de **medicamentos** (Brasil). Perfil
  de aplicação: não cita empresa. Alimentos e outros setores ficam fora.
- **Perfil:** `compliance-profile-farma-anvisa.json`, na mesma pasta.
- **Leitura primária:** 28/09/2026. Fontes (URL, data de acesso) e vigência de cada norma: `C:\Users\fabriciosouza\metacognition-framework\docs\specs\b3-documentacao-regulada\fontes.md`, seção 6.
- **Siglas das normas:**
  - IN134 = IN nº 134/2022 (sistemas computadorizados);
  - IN138 = IN nº 138/2022 (qualificação e validação);
  - RDC658 = RDC nº 658/2022 (BPF de medicamentos);
  - G33 = Guia nº 33/2020 v1. O G33 é **não vinculante** e a base legal dele cita normas revogadas em 2022.
- **Marcas:**
  - **CONFIRMADO:** o trecho foi lido no texto oficial.
  - **INFERIDO:** só há fonte secundária.
  - **DESCONHECIDO:** o trecho não foi achado.
  - **NÃO SE APLICA:** peça de gestão do projeto, que a norma não pede.
- **Regra de manutenção:** toda peça do perfil precisa ter pelo menos uma linha aqui, com a coluna Peça escrita igual ao
  perfil. As peças são:
  - as peças de `categorias_software`;
  - os tipos de `documentos` e os `itens` de cada tipo;
  - os `testes_obrigatorios_com_impacto`.

  Quem confere é `python tools/regulado.py mapa <perfil.json>`, rodado pelo canário `test_regulado`.

## Peças de gestão do projeto (kit comum)

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `TAP` | — | — | peça de gestão do projeto | NÃO SE APLICA |
| `especificacao` | — | — | arquivo único do projeto; os requisitos dele alimentam a ERU | NÃO SE APLICA |
| `HANDOFF` | — | — | peça de gestão do projeto | NÃO SE APLICA |
| `glossario` | — | — | peça de gestão do projeto | NÃO SE APLICA |
| `cronograma` | — | — | peça de gestão do projeto | NÃO SE APLICA |

## Peças do ciclo de validação

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `ERU` | IN134 | art. 20, caput | "As especificações dos requerimentos dos usuários devem descrever as funções requeridas ao sistema computadorizado e se basearem em uma avaliação de risco documentada" | CONFIRMADO |
| `ERU` | IN138 | art. 27, caput e § 2º | "A especificação para equipamentos, instalações, utilidades ou sistemas deve ser definida em uma ERU e/ou especificação funcional." · "A ERU deve ser um ponto de referência ao longo do ciclo de vida da validação." | CONFIRMADO |
| `ERU` | IN138 | art. 28, parágrafo único | "Os requisitos da ERU devem ser verificados durante a Qualificação de Projeto." | CONFIRMADO |
| `analise-de-risco` | IN134 | art. 8º; art. 9º | "A gestão de riscos deve ser aplicada durante todo o ciclo de vida do sistema computadorizado" · "As decisões sobre a extensão da validação e controle de integridade de dados devem ser baseadas e justificadas em avaliações de risco documentadas" | CONFIRMADO |
| `analise-de-risco` | IN138 | art. 5º, caput | "as decisões sobre o escopo e a extensão da qualificação e validação devem se basear em uma avaliação de risco justificada e documentada" | CONFIRMADO |
| `especificacao-funcional` | IN138 | art. 27, caput | "deve ser definida em uma ERU e/ou especificação funcional." | CONFIRMADO |
| `especificacao-funcional` | G33 | 9.5.1 | "para alguns sistemas, como aqueles comercialmente disponíveis e de baixo risco, pertencentes à categoria 3 [...] um documento contendo as especificações funcionais não é necessário." | CONFIRMADO |
| `especificacao-de-configuracao` | IN134 | art. 34 | "Quaisquer alterações em um sistema computadorizado, incluindo configurações do sistema, devem ser feitas de maneira controlada, de acordo com um procedimento definido." | CONFIRMADO |
| `especificacao-de-configuracao` | G33 | 9.6.1 | "Dependendo do tipo de sistema (configurável ou customizado), as especificações de configuração e de projeto fornecem uma expansão técnica detalhada das especificações funcionais." | CONFIRMADO |
| `especificacao-de-projeto` | G33 | 9.6.1 | "Não há necessidade de preparação de documentos separados para definição da configuração e do projeto." | CONFIRMADO |
| `especificacao-de-projeto` | IN134 | art. 22 | "Para a validação de sistemas computadorizados personalizados, ou sob medida, deve haver um processo que garanta a avaliação formal e o registro das medidas de qualidade e de desempenho [...]" (o nome "especificação de projeto" só aparece no G33) | CONFIRMADO |
| `matriz-requisito-teste` | IN134 | art. 20, parágrafo único | "Os requisitos do usuário devem ser rastreáveis durante todo o ciclo de vida." | CONFIRMADO |
| `matriz-requisito-teste` | G33 | 9.8.5 | "[...] é conhecida como Matriz de Rastreabilidade dos Requisitos" (o termo "matriz" não aparece nas normas vinculantes) | CONFIRMADO |
| `matriz-requisito-risco-teste` | IN134 | art. 20, parágrafo único; art. 9º | rastreabilidade dos requisitos + extensão da validação justificada pelo risco documentado | CONFIRMADO |
| `matriz-requisito-risco-teste` | G33 | 9.8.5 | "A rastreabilidade deve focar nos aspectos críticos para a segurança do paciente, qualidade do produto e integridade dos dados" | CONFIRMADO |
| `roteiro-de-testes` | IN134 | art. 23, caput e § 1º | "Devem ser demonstradas as evidências dos métodos e cenários de testes apropriados." · "devem incluir os limites de parâmetros do sistema (processo), limites de dados e tratamento de erros." | CONFIRMADO |
| `roteiro-de-testes` | IN138 | art. 18; art. 3º, XVI | "Devem ser preparados protocolos de validação que definam os sistemas, atributos e parâmetros críticos e os critérios de aceitação associados." (a definição de protocolo inclui "sistema computadorizado") | CONFIRMADO |
| `relatorio-de-testes` | IN134 | art. 23, caput | "Devem ser demonstradas as evidências dos métodos e cenários de testes apropriados." | CONFIRMADO |
| `relatorio-de-testes` | RDC658 | art. 175, parágrafo único | "Os resultados e conclusões dos estudos de validação devem ser registrados." | CONFIRMADO |
| `relatorio-de-validacao` | IN138 | art. 23, caput; art. 24, caput | "A revisão e as conclusões da validação devem ser relatadas e os resultados obtidos devem ser resumidos em relação aos critérios de aceitação." · "Uma liberação formal para a próxima etapa [...] deve ser autorizada pela pessoa apropriada, como parte da aprovação do relatório de validação" | CONFIRMADO |
| `relatorio-de-validacao` | IN134 | art. 15; art. 17 | "Os documentos e relatórios de validação devem abranger as etapas relevantes do ciclo de vida." · "A documentação de validação deve incluir os registros dos controles de mudança e os relatórios de investigação de quaisquer desvios observados." | CONFIRMADO |
| `descricao-do-sistema` | IN134 | art. 19 | "Devem estar disponíveis descrições atualizadas dos sistemas críticos que detalhem os arranjos físicos e lógicos, fluxos de dados e interfaces com outros sistemas" | CONFIRMADO |
| `gestao-de-mudanca` | IN134 | art. 34; art. 17 | "Quaisquer alterações em um sistema computadorizado, incluindo configurações do sistema, devem ser feitas de maneira controlada, de acordo com um procedimento definido." | CONFIRMADO |
| `gestao-de-mudanca` | RDC658 | art. 8º, XII | "estejam implementados procedimentos para a avaliação prospectiva de mudanças planejadas e sua aprovação antes da implementação" | CONFIRMADO |
| `inventario` | IN134 | art. 18 | "Um inventário de todos os sistemas relevantes e as funcionalidades relacionadas às Boas Práticas de Fabricação deve ser mantido pela empresa e disponibilizada sempre que solicitado." | CONFIRMADO |

## Documentos emitidos pelo perfil

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `eru` | IN134 | art. 20, caput | mesma base da peça `ERU` acima | CONFIRMADO |
| `relatorio-de-validacao` | IN138 | art. 23; art. 24 | mesma base da peça `relatorio-de-validacao` acima | CONFIRMADO |
| `checklist-de-prontidao` | IN138 | art. 24, caput | "Uma liberação formal para a próxima etapa [...] deve ser autorizada pela pessoa apropriada" — a forma de checklist é do framework; cada item tem a sua base abaixo | CONFIRMADO |

## Itens do checklist de prontidão

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `Descrição do sistema` | IN134 | art. 19 | "Devem estar disponíveis descrições atualizadas dos sistemas críticos [...]" | CONFIRMADO |
| `POPs` | IN134 | art. 34 | "[...] de acordo com um procedimento definido." | CONFIRMADO |
| `POPs` | RDC658 | art. 119, caput; art. 120, § 2º | "Os documentos contendo instruções devem ser aprovados, assinados e datados por pessoas apropriadas e autorizadas." · "Os Procedimentos Operacionais Padrão, as Instruções de Trabalho e os Métodos devem ser escritos preferencialmente no modo imperativo." | CONFIRMADO |
| `Treinamento` | RDC658 | art. 25 | "Todo o pessoal deve estar ciente dos princípios das Boas Práticas de Fabricação que os afetam e receber treinamento inicial e contínuo" | CONFIRMADO |
| `Treinamento` | IN134 | art. 10 | "[...] devem ter qualificações adequadas, nível de acesso e responsabilidades definidas para desempenhar as suas atribuições." | CONFIRMADO |
| `Controle de acesso` | IN134 | art. 36; art. 38 | "Devem existir controles físicos ou lógicos que assegurem que o acesso ao sistema computadorizado é permitido apenas às pessoas autorizadas." · "A criação, a alteração e o cancelamento de autorizações de acesso devem ser registradas." | CONFIRMADO |
| `Backup e restauração` | IN134 | art. 30, caput e parágrafo único | "Devem ser feitos backups de todos os dados relevantes." · "a capacidade de restaurar os dados devem ser verificadas durante a validação e monitoradas periodicamente" | CONFIRMADO |
| `Continuidade` | IN134 | art. 44, caput e § 2º | "Devem existir medidas que garantam a continuidade dos processos críticos em caso de falhas dos sistemas computadorizados" · "devem ser adequadamente documentadas e testadas." | CONFIRMADO |
| `Revisão periódica` | IN134 | art. 35, caput | "Sistemas computadorizados devem ser periodicamente avaliados para confirmação de que permanecem validados e em conformidade com as Boas Práticas de Fabricação." | CONFIRMADO |

## Testes obrigatórios com impacto

| Peça | Norma | Artigo/item | Trecho literal | Marca |
|---|---|---|---|---|
| `integridade de dados` | IN134 | art. 26; art. 28; art. 32; art. 39 | "verificação adicional da exatidão dos dados" · "verificados quanto à acessibilidade, legibilidade e exatidão" · "indicando se algum dos dados foi alterado desde a sua inserção original" · "registrar a identidade dos usuários que inserem, alteram, confirmam ou excluem dados, incluindo data e hora" | CONFIRMADO |
| `integridade de dados` | RDC658 | art. 116; art. 124; art. 125 | "precisão, integridade, disponibilidade e legibilidade dos documentos" · "Os registros devem ser realizados ou completados sempre que uma ação for realizada" · "devendo permitir a leitura da informação original" | CONFIRMADO |
| `trilha de auditoria` | IN134 | art. 33, caput e §§ 1º a 3º | "Baseada em análise de risco, deve ser considerada a construção de um sistema de trilha de auditoria [...]" · "As trilhas de auditoria devem ser revisadas regularmente." — a norma pede que a trilha seja **considerada** com base no risco; o registro de quem, quando e o quê (art. 39) é incondicional | CONFIRMADO |
| `controle de acesso` | IN134 | art. 36; art. 37; art. 38 | "A extensão dos controles de segurança deve ser determinada de acordo com uma avaliação da criticidade" | CONFIRMADO |
| `backup/restauração` | IN134 | art. 30; art. 45, parágrafo único | "a capacidade de recuperar os dados deve ser assegurada e testada." | CONFIRMADO |

## O que a norma não traz (não citar como exigência)

- **Categorias de software 1, 3, 4 e 5 (GAMP):** existem só no G33 (itens 7.2 e 7.3), que é não vinculante. As normas
  vinculantes só distinguem "software comercial pronto para uso" (IN134, art. 3º, VIII; art. 13) de sistema
  "personalizado ou sob medida" (IN134, art. 3º, VII; art. 22). No perfil, a categoria serve para escalonar as peças,
  não para citar exigência.
- **ALCOA / ALCOA+:** a sigla não aparece em nenhum dos quatro textos. As palavras "atribuível" e "contemporâneo"
  também não aparecem. Os atributos estão nos artigos da linha `integridade de dados`.
- **Assinatura eletrônica:** é facultativa ("podem ser assinados", IN134, art. 41). Quando usada, segue o art. 42. Na
  liberação de lote por sistema, a identificação do responsável é por assinatura eletrônica (art. 43, § 2º).
