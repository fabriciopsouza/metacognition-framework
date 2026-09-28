# B3 — Fontes regulatórias (pesquisa de 25/09/2026)

- **Objeto:** requisitos de documentação para sistemas computadorizados em indústria farmacêutica (ANVISA).
- **Método:** agente de pesquisa isolado (Sonnet), só leitura, web. Marcas: CONFIRMADO = lido na fonte primária · TRIANGULADO = ≥2 fontes secundárias convergentes, primária não lida · INFERIDO · DESCONHECIDO.
- **Uso:** base da Parte C de `C:\Users\fabriciosouza\metacognition-framework\docs\specs\b3-documentacao-regulada\spec.md`.

## 1. Normas vigentes

| # | Norma | Data / vigência | Substitui | Marca | Fonte primária |
|---|---|---|---|---|---|
| N1 | RDC nº 658/2022 — BPF de medicamentos | 30/03/2022; vigente 02/05/2022 | RDC 301/2019 (art. 379) | CONFIRMADO (texto integral em 28/09/2026; seção 6) | https://sindusfarma.org.br/uploads/files/8e1f-diego-silva/2022/Anvisa/RDC%20BPF%20-%20Anvisa/file.pdf |
| N2 | IN nº 134/2022 — sistemas computadorizados | 30/03/2022; vigente 02/05/2022 | IN 43/2019 | CONFIRMADO em 28/09/2026 (texto integral; seção 6) | https://www.legisweb.com.br/legislacao/?id=429571 |
| N3 | IN nº 138/2022 — qualificação e validação | 30/03/2022 | IN 47/2019 | CONFIRMADO em 28/09/2026 (texto integral; seção 6) | https://www.legisweb.com.br/legislacao/?id=429593 |
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

Situação em 28/09/2026, depois da leitura primária da seção 6:

1. Artigo exato da RDC 658/2022 que revoga a RDC 301/2019. **Resolvida:** art. 379.
2. Guia ANVISA numerado de integridade de dados. Continua não localizado.
3. Sigla ALCOA/ALCOA+ no texto oficial. **Resolvida:** está ausente das IN 134, IN 138, RDC 658 e do Guia 33, conforme busca literal no texto integral.
4. Nota técnica alinhando N4 ao pacote de 2022. Continua não localizada.
5. Texto primário integral de N2 e N3. **Resolvida:** lidos no AnvisaLegis e conferidos no DOU.
6. Capítulo da RDC 658/2022 sobre sistemas computadorizados. **Resolvida:** lidos os arts. 116 a 126 (documentação e registros) e os arts. 8º, 21, 25 e 175.
7. Texto primário do FDA CSA. Continua não lido. É referência de mercado e não entra no perfil.
8. Cobertura das seções §9.x de N4. **Resolvida:** íntegra do PDF lida (itens 9.3.1, 9.5.1, 9.6.1, 9.8.5 e 9.9.1 citados no mapa).

## 6. Leitura primária (28/09/2026)

- **Método:** agente de pesquisa isolado, só leitura. Texto integral baixado do AnvisaLegis e do PDF do Guia, lido por busca literal. 11 trechos foram conferidos também no DOU, e todos batem. O autor conferiu por amostragem o número dos arts. 18, 20, 22, 33, 35, 41 e 44 da IN 134, dos arts. 24, 27 e 40 da IN 138 e dos arts. 25, 124, 175 e 379 da RDC 658.
- **Resultado:** todo tema pesquisado tem base CONFIRMADA em texto oficial. Só a categorização de software não tem base em norma vinculante.
  1. ERU;
  2. análise e gestão de risco;
  3. validação (plano, protocolos, relatório, migração de dados);
  4. matriz de rastreabilidade: a norma exige a rastreabilidade; o termo "matriz" só aparece no Guia 33;
  5. descrição do sistema;
  6. inventário;
  7. gestão de mudança e de configuração;
  8. integridade de dados;
  9. trilha de auditoria;
  10. controle de acesso e segurança;
  11. backup e restauração;
  12. continuidade;
  13. revisão periódica;
  14. assinatura eletrônica;
  15. avaliação de fornecedor;
  16. categorização de software: só no Guia 33, não vinculante.
- **O que o canário confere:** as peças do perfil, e não estes temas. `regulado.py mapa` exige uma linha por peça no mapa, e no mapa toda linha com norma citada está CONFIRMADO.
- **Peça → artigo, com o trecho literal:** `C:\Users\fabriciosouza\metacognition-framework\exemplos\dominio-regulado\farma-anvisa-mapa-normas.md`.

### Vigência em 28/09/2026

| Norma | DOU | Vigor | Situação (AnvisaLegis) | Alterações |
|---|---|---|---|---|
| IN nº 134/2022 | 31/03/2022, ed. 62, seção 1, p. 361 | 02/05/2022 (art. 48) | Vigente | nenhuma; revogou a IN 43/2019 (art. 47) |
| IN nº 138/2022 | 31/03/2022, ed. 62, seção 1, p. 367 | 02/05/2022 (art. 133) | Vigente | nenhuma; revogou a IN 47/2019 (art. 132) |
| RDC nº 658/2022 | 31/03/2022, ed. 62, seção 1, p. 320 | 02/05/2022 (art. 380) | Vigente com alterações | só a RDC nº 972/2025 (DOU 23/04/2025, vigor na publicação) mudou o art. 372 (controle on-line na embalagem); nenhum artigo de sistemas computadorizados mudou; revogou a RDC 301/2019 (art. 379) |
| Guia nº 33/2020 v1 | publicado em 13/04/2020 | 14/04/2020 | Vigente | sem versão 2; "não normativo, de caráter recomendatório e não vinculante"; base legal cita normas revogadas em 2022 |

### Divergências com fontes secundárias
- **RDC 972/2025:** fontes secundárias diziam que ela flexibilizou a qualificação de transportadoras e que o vigor começou em 06/05/2025. O texto oficial tem 3 artigos, não trata de transportadoras e vigora desde a publicação, em 23/04/2025.
- **Trilha de auditoria:** a IN 134, art. 33, diz que ela "deve ser considerada" com base em risco; não é exigência incondicional.
- **Assinatura eletrônica:** é facultativa pela IN 134, art. 41. O perfil passou a marcá-la como exigida "quando usada".

### URLs (acesso em 28/09/2026)

1. IN 134/2022, AnvisaLegis: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=INM&numeroAto=00000134&seqAto=000&valorAno=2022&orgao=DC/ANVISA/MS&codTipo=&desItem=&desItemFim=&cod_menu=9434&cod_modulo=310&pesquisa=true
2. IN 134/2022, DOU: https://www.in.gov.br/en/web/dou/-/instrucao-normativa-in-n-134-de-30-de-marco-de-2022-389839479
3. IN 138/2022, AnvisaLegis: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=INM&numeroAto=00000138&seqAto=000&valorAno=2022&orgao=DC/ANVISA/MS&codTipo=&desItem=&desItemFim=&cod_menu=9434&cod_modulo=310&pesquisa=true
4. IN 138/2022, DOU: https://www.in.gov.br/en/web/dou/-/instrucao-normativa-in-n-138-de-30-de-marco-de-2022-389932120
5. RDC 658/2022, AnvisaLegis: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=RDC&numeroAto=00000658&seqAto=000&valorAno=2022&orgao=RDC%2FDC%2FANVISA%2FMS&codTipo=&desItem=&desItemFim=&cod_menu=1696&cod_modulo=134&pesquisa=true
6. RDC 658/2022, DOU: https://www.in.gov.br/en/web/dou/-/resolucao-rdc-n-658-de-30-de-marco-de-2022-389846242
7. RDC 972/2025, AnvisaLegis: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=RDC&numeroAto=00000972&seqAto=000&valorAno=2025&orgao=RDC/DC/ANVISA/MS&codTipo=&desItem=&desItemFim=&cod_menu=1696&cod_modulo=134&pesquisa=true
8. RDC 972/2025, ficha: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&link=S&tipo=RDC&numeroAto=00000972&seqAto=222&valorAno=2025&orgao=ANVISA%2FMS&codTipo=&desItem=&desItemFim=&cod_modulo=134&cod_menu=1696
9. Guia 33/2020, ficha: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=GUI&numeroAto=00000033&seqAto=222&valorAno=2020&orgao=ANVISA%2FMS&codTipo=&desItem=&desItemFim=&cod_menu=9483&cod_modulo=644&pesquisa=true
10. Guia 33/2020, íntegra (PDF, 104 p.): https://anexosportal.datalegis.net/arquivos/1860250.pdf
11. DOU de 31/03/2022, seção 1: https://www.in.gov.br/leiturajornal?data=31-03-2022&secao=do1

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
