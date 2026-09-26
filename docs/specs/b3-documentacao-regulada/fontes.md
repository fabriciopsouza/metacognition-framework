# B3 — Fontes regulatórias (pesquisa de 25/09/2026)

- **Objeto:** requisitos de documentação para sistemas computadorizados em indústria farmacêutica (ANVISA).
- **Método:** agente de pesquisa isolado (Sonnet), só leitura, web. Marcas: CONFIRMADO = lido na fonte primária · TRIANGULADO = ≥2 fontes secundárias convergentes, primária não lida · INFERIDO · DESCONHECIDO.
- **Uso:** base da Parte C de `C:\Users\fabriciosouza\metacognition-framework\docs\specs\b3-documentacao-regulada\spec.md`.

## 1. Normas vigentes

| # | Norma | Data / vigência | Substitui | Marca | Fonte primária |
|---|---|---|---|---|---|
| N1 | RDC nº 658/2022 — BPF de medicamentos | 30/03/2022; vigente 02/05/2022 | RDC 301/2019 (artigo de revogação: DESCONHECIDO) | CONFIRMADO (p. 1–8 lidas) | https://sindusfarma.org.br/uploads/files/8e1f-diego-silva/2022/Anvisa/RDC%20BPF%20-%20Anvisa/file.pdf |
| N2 | IN nº 134/2022 — sistemas computadorizados | 30/03/2022; vigente 02/05/2022 | IN 43/2019 | TRIANGULADO (4 fontes; primária não lida) | https://www.legisweb.com.br/legislacao/?id=429571 |
| N3 | IN nº 138/2022 — qualificação e validação | 30/03/2022 | IN 47/2019 | TRIANGULADO (2 fontes) | https://www.legisweb.com.br/legislacao/?id=429593 |
| N4 | Guia ANVISA nº 33/2020 v1 — validação de sistemas computadorizados | 26/03/2020; vigente 14/04/2020 | guia homônimo de 04/2010 | CONFIRMADO (p. 1–32, 54–60, 73–83 lidas) | https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/medicamentos/publicacoes-sobre-medicamentos/guia-de-validacao-de-sistemas-computadorizados.pdf |
| R1 | GAMP 5, 2ª ed. (ISPE, 07/2022) | referência de mercado, não norma | GAMP 5 1ª ed. | INFERIDO (texto pago não lido) | — |
| R2 | FDA Computer Software Assurance (final 24/09/2025) | referência de mercado, não vinculante no Brasil | seção 6 do "General Principles of Software Validation" | TRIANGULADO | https://www.federalregister.gov/documents/2025/09/24/2025-18468/computer-software-assurance-for-production-and-quality-system-software-guidance-for-industry-and |

**Achado:** a base legal do Guia 33/2020 (§3) cita RDC 301/2019, IN 43/2019 e IN 47/2019 — revogadas em 2022. Não citar essas normas em documento novo. Nota técnica de atualização do guia: não localizada (DESCONHECIDO).

## 2. Entregáveis esperados em inspeção

| Entregável | Base | Obrigatoriedade | Quando |
|---|---|---|---|
| Inventário de sistemas | N4 §8, §10 | boa prática forte | sempre |
| Política / plano mestre de validação | N4 §9.1 | expectativa de inspeção | corporativo |
| Plano de validação por sistema | N4 §9.2 | proporcional ao risco (plano genérico aceito para sistemas semelhantes) | sistema novo; mudança maior |
| ERU / URS | N4 §9.3 | obrigatório na substância; profundidade pelo risco e pela categoria | categorias 3, 4, 5 |
| Avaliação de fornecedor | N4 §9.4 | proporcional ao risco (básica → questionário → auditoria); não fazer exige justificativa formal | aquisição; reavaliação se crítico |
| Especificação funcional / de configuração / de projeto | N4 §9.5–9.6; §7.3 | categorias 4 e 5; dispensável na 3 | sistema novo |
| Gestão de risco (inicial e funcional) | N4 §6 (ICH Q9) | obrigatório na substância; formalidade pelo risco | ciclo de vida |
| Categorização GAMP (1, 3, 4, 5) | N4 §7 | ferramenta de escalonamento | sistema novo; mudança |
| Matriz de rastreabilidade | N4 §9.8.5 | obrigatória; categoria 3: requisito → teste; 4/5: cadeia completa | sistema novo |
| Plano, protocolos e relatório de testes | N4 §9.7, Tab. 1 (terminologia livre) | obrigatório | sistema novo; mudança relevante |
| Descrição do sistema | N4 §9.8.1.1 | obrigatório, atualizada | antes da liberação |
| Gestão de configuração e mudança | N4 §9.8.2, §11.7 | obrigatório | projeto e operação |
| Relatório de validação | N4 §9.9 (aprovação: dono do processo + Qualidade) | obrigatório | encerramento |
| POPs | N4 §9.2.2.9, §11 | obrigatório | operação |
| Treinamento | N4 §9.2.2.10, §9.9.2.8 | obrigatório | sistema novo e contínuo |
| Revisão periódica | N4 §11.9 | obrigatório; frequência pelo risco | operação |
| Backup e restauração (com teste de restauração) | N4 §11.10 | obrigatório | operação |
| Continuidade / recuperação de desastre | N4 §11.11; N2 | obrigatório para sistemas críticos | operação |
| Segurança e controle de acesso | N4 §11.12 | obrigatório | operação |
| Gestão de registros (retenção, arquivo, recuperação) | N4 §11.14 | obrigatório | operação e aposentadoria |
| Migração de dados | N4 §12 | obrigatório quando ocorre | troca de sistema |
| Aposentadoria | N4 §13 | obrigatório | fim de vida |
| Integridade de dados | N2 (vinculante) | obrigatório por norma | todo o ciclo |

## 3. Base para trabalho ágil (citações de N4)

- §4.1.3 — atividades do ciclo de vida escalonadas por impacto, complexidade, avaliação do fornecedor e impacto no negócio.
- §6.3.1 — *"pode não ser necessário realizar as etapas subsequentes se o risco já estiver em um nível aceitável."*
- §7.3.2 — categoria 3: ciclo simplificado; *"A verificação consiste basicamente em uma fase de testes única."*
- p. 2 — *"instrumento regulatório não normativo, de caráter recomendatório e não vinculante"*.
- §6.1 — gestão de risco é *"um processo iterativo utilizado durante todo o ciclo de vida"*. Termo "ágil" não localizado nas páginas lidas.

## 4. Lacunas

1. Artigo exato da RDC 658/2022 que revoga a RDC 301/2019 — DESCONHECIDO.
2. Guia ANVISA numerado de integridade de dados — não localizado.
3. Sigla ALCOA/ALCOA+ no texto oficial (N1, N2, N4) — não localizada; aparece só em fontes secundárias.
4. Nota técnica alinhando N4 ao pacote de 2022 — não localizada.
5. Texto primário integral de N2 e N3 — não lido.
6. Capítulo da RDC 658/2022 sobre sistemas computadorizados — não lido.
7. Texto primário do FDA CSA — não lido com sucesso.
8. Páginas lidas de N4 (1–32, 54–60, 73–83) × seções §9.x citadas: cobertura exata a conferir (apontado pela revisão adversarial de 25/09).

## 5. URLs consultadas

1. https://sindusfarma.org.br/uploads/files/8e1f-diego-silva/2022/Anvisa/RDC%20BPF%20-%20Anvisa/file.pdf
2. https://sindusfarma.org.br/uploads/files/8e1f-diego-silva/2022/Anvisa/RDC%20BPF%20-%20Anvisa/file%20-%20Copy%208.pdf
3. https://www.legisweb.com.br/legislacao/?id=477077
4. https://www.legisweb.com.br/legislacao/?id=429571
5. https://www.legisweb.com.br/legislacao/?id=429593
6. https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=INM&numeroAto=00000134&seqAto=000&valorAno=2022&orgao=DC/ANVISA/MS
7. https://www.fukumaadvogados.com.br/wp-content/uploads/2022/03/IN-N%C2%BA-134-DE-30.03.2022-.pdf
8. https://www.latinigroup.com.br/index.php/em-foco/legislacao/597-instrucao-normativa-in-n-134-de-30-de-marco-de-2022
9. https://fitoterapiabrasil.com.br/legislacao/no-134-de-30-de-marco-de-2022
10. https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/medicamentos/publicacoes-sobre-medicamentos/guia-de-validacao-de-sistemas-computadorizados.pdf
11. https://www.gmp-compliance.org/files/eca/userFiles/publications/Guia-para-Validacao-de-Sistemas-Computadorizados.pdf
12. https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/17751
13. https://blog.softexpert.com/en/in-134/
14. https://blog.softexpert.com/en/rdc-658-22-good-manufacturing-practices-for-medicines/
15. https://fivevalidation.com/pt-br/principais-mudancas-da-rdc-301-2019-para-a-resolucao-658-2022/
16. https://fivevalidation.com/pt-br/novo-guia-para-validacao-de-sistemas-computadorizados-anvisa/
17. https://consultoriamd.com.br/blog/guia-no-33-2020-versao-1-uma-avaliacao-do-cenario-da-validacao-de-sistemas-computadorizados/
18. https://www.scilife.io/blog/gamp5-for-gxp-compliant-computerized-systems
19. https://www.scilife.io/blog/gamp-5-and-gamp-5-2nd-edition-differences
20. https://casrai.org/guides/gamp-5-second-edition-changes
21. https://focus.pqegroup.com/en/csv-data-integrity/gamp-5v2-critical-thinking-ai
22. https://www.federalregister.gov/documents/2025/09/24/2025-18468/computer-software-assurance-for-production-and-quality-system-software-guidance-for-industry-and
23. https://www.nsf.org/life-science-regulatory-news/fda-final-guidance-computer-software-assurance-csa
24. https://gmpinsiders.com/fda-2025-guidance-csa/
25. https://www.farmaceuticas.com.br/wp-content/uploads/2017/10/SINDUSFARMA_Manual_Integridade_de_Dados-1.pdf

Lista integral (70 URLs) e PDFs baixados: registro do agente de pesquisa de 25/09/2026; PDFs em `C:\Users\fabriciosouza\.claude\projects\c--Users-fabriciosouza-metacognition-framework\07b1825e-c78c-4c3d-9e3d-239036d9788d\tool-results\` (Guia 33/2020, 103 p.; RDC 658/2022).
