# Perfil anp-combustiveis — pesquisa de normas (28/09/2026)

- **Escopo:** distribuição e abastecimento de combustíveis líquidos (Brasil). Não cita empresa.
- **Método:** 3 agentes de pesquisa isolados, só leitura, consultando a web em 28/09/2026. Eles leram o texto oficial em:
  - DOU (in.gov.br, pesquisa.in.gov.br);
  - planalto.gov.br, gov.br/anp, gov.br/inmetro;
  - CONFAZ, portal da NF-e e anttlegis.
- **Fontes que não abriram:**
  - legislacao.anp.gov.br e simp.anp.gov.br: o endereço não resolveu;
  - atosoficiais.com.br, o texto consolidado oficial da ANP: acesso negado (403).

  Por isso as alterações posteriores foram vistas no LegisWeb (secundário) e ficam INFERIDO.
- **Marcas:**
  - CONFIRMADO = lido no texto oficial;
  - INFERIDO = fonte secundária, ou vigência deduzida por ausência de ato revogador;
  - DESCONHECIDO = não achado.
- **Situação:** consolidado pelo autor a partir dos relatórios das frentes. Revisado por QA adversarial (ADR-128); marcas das Res. 807, 884 e 898 rebaixadas a INFERIDO até a reconferência no in.gov.br.

## 1. Achado principal

**A ANP não tem norma que exija do distribuidor validação de sistemas computadorizados, integridade de dados ou trilha de auditoria.** A busca foi negativa nos textos oficiais e nos dois manuais do i-SIMP (Geral v01/2025; Distribuidores v1.3, 06/04/2020).

A integridade citada na Res. 729/2018, art. 3º, e na Res. 868/2022, art. 8º, é obrigação da ANP sobre os dados recebidos, não do distribuidor.

O controle indireto que alcança o distribuidor é duplo:
- a Lei 9.847/1999, art. 3º, V, pune adulterar ou alterar registros;
- a Res. 950/2023, art. 22, IX, exige registros "escriturados e atualizados".

Marca: DESCONHECIDO (busca negativa).

## 2. Normas e vigência

| Norma | Tema | Vigência | Marca |
|---|---|---|---|
| Lei 9.847/1999 | abastecimento de utilidade pública; penalidades (art. 3º) | vigente | CONFIRMADO |
| Lei 9.478/1997 | ANP regula e autoriza o abastecimento (art. 8º, XV) | vigente | CONFIRMADO |
| Res. ANP 950/2023 | autorização e obrigações do distribuidor; revogou a 58/2014 | desde 10/04/2024; alterações de 968/2024, 972/2024, 977/2024, 994/2026 e 997/2026 vistas no LegisWeb; Consulta Pública 20/2026 propõe mudanças | CONFIRMADO (DOU 09/10/2023, p. 94–97); alterações INFERIDO |
| Res. ANP 729/2018 | remessa mensal de dados ao i-SIMP | desde 180 dias após 14/05/2018; nenhum ato revogador achado; o manual de 2025 ainda a cita | texto CONFIRMADO; vigência INFERIDO |
| Res. ANP 868/2022 | estoque diário (IEngine) | desde 01/03/2022 | texto CONFIRMADO; vigência INFERIDO |
| Res. ANP 949/2023 | estoque mínimo; revogou a 45/2013 | desde 10/04/2024 | CONFIRMADO |
| Res. ANP 894/2022 | coeficiente de correção a 20 °C (densidade e volume); revogou a CNP 6/1970 | desde 01/12/2022 | CONFIRMADO |
| Res. ANP 807/2020 | especificação da gasolina; boletim de conformidade do distribuidor | vigente; alterada pela 988/2025 (E30) | INFERIDO (cópia sem URL de origem); alteração INFERIDO |
| Res. ANP 968/2024 | especificação do diesel; revogou a 50/2013 | desde 31/07/2024; art. 13 suspenso pela 978/2024 | CONFIRMADO |
| Res. ANP 907/2022 | especificação do etanol | desde 01/12/2022 | CONFIRMADO; vigência INFERIDO |
| Res. ANP 828/2020 | conteúdo dos documentos da qualidade | vigente; alterada por 968/2024, 980/2025 e 997/2026 | CONFIRMADO |
| Res. ANP 898/2022 | lacre do caminhão-tanque e amostra-testemunha; revogou a 9/2007 | desde 01/12/2022 | INFERIDO (cópia sem URL de origem; reconferir no in.gov.br) |
| Res. ANP 884/2022 | livro de movimentação de combustíveis (LMC) do **posto**; variação de 0,6%; revogou a Portaria DNC 26/1992 | desde 03/10/2022 | INFERIDO (cópia sem URL de origem; reconferir no in.gov.br) |
| Res. Conjunta ANP/INMETRO 1/2013 | medição de petróleo e gás natural | vigente; **não se aplica a derivados líquidos** (item 1.2.3.2) | INFERIDO (LegisWeb) |
| Convênio ICMS 110/07 | fator de correção de volume (FCV); o distribuidor fatura à temperatura ambiente (cláusula nona, §§ 5º e 8º) | vigente | CONFIRMADO (CONFAZ) |
| NT NF-e 2023.001 | grupo combustível da NF-e (`qTemp`, `pBio`, `origComb`) | vigente | CONFIRMADO |
| Res. ANTT 5.998/2022 | transporte rodoviário de produtos perigosos; documentos da carga (art. 23) | desde 01/06/2023; alterada por 6.016/2023 e 6.056/2024 | CONFIRMADO |
| Portaria INMETRO 291/2021 | sistemas de medição dinâmica (medidores); revogou a 64/2003 | vigente; alterada pela 656/2025 | INFERIDO (LegisWeb) |
| Portaria INMETRO 227/2022 | bombas medidoras; revogou a 559/2016 | desde 01/07/2022; alterada pela 587/2022 | CONFIRMADO |
| Portaria INMETRO 49/2022 | veículo-tanque; revogou a 208/2016 | desde 01/06/2022 | CONFIRMADO |
| Portaria INMETRO 103/2022 | arqueação de tanque fixo (também as 160/2022 e 471/2021) | vigente (página do INMETRO de 09/09/2026) | CONFIRMADO |
| Portarias INMETRO 89/2021 e 86/2021 | densímetro de vidro; termômetro de líquido em vidro | vigentes (lista da Portaria 630/2023) | CONFIRMADO |

## 3. Peça candidata → norma → trecho literal

| Peça candidata | Norma e artigo | Trecho literal | Marca |
|---|---|---|---|
| envio mensal ao i-SIMP | Res. 950/2023, art. 23; Res. 729/2018, art. 2º | "deverá enviar, até o dia quinze e cada mês, a informação sobre sua comercialização [...] por meio do aplicativo do I-Simp" (o "e" é erro do próprio DOU) · "devem ser enviadas mensalmente à ANP, até o dia quinze do mês subsequente" · §6º: declarar "mesmo que não tenha ocorrido movimentação" | CONFIRMADO |
| reprocessamento do i-SIMP | Res. 729/2018, art. 2º, §§ 4º e 5º | "O arquivo de reprocessamento tem a mesma natureza do originalmente apresentado, substituindo-o integralmente." | CONFIRMADO |
| sanção por falta de envio | Res. 950/2023, art. 23 §2º; art. 24, II, "e" | 2 meses sem envio levam à interdição; 3 meses consecutivos, à revogação da autorização | CONFIRMADO |
| estoque diário | Res. 868/2022, arts. 3º e 4º | "em todos os dias úteis, por meio do sistema de processamento de arquivos da ANP - IEngine" · "até às 12 horas (horário de Brasília) do dia útil seguinte ao fechamento do estoque" | CONFIRMADO |
| estoque mínimo | Res. 949/2023, arts. 2º e 6º | "EmínimoD = KD (CD/30)"; CD vem dos dados do I-Simp | CONFIRMADO |
| guarda e disponibilidade de registros | Res. 950/2023, art. 22, IX | "pelo prazo de seis meses, todos os registros de movimentação e estoques [...] escriturados e atualizados, bem como as notas fiscais" | CONFIRMADO |
| correção a 20 °C | Res. 894/2022, art. 1º | "estabelece [...] o coeficiente de correção para temperatura de 20°C, da densidade (massa específica) e do volume" (Tabelas I e II no site da ANP) | CONFIRMADO |
| volume na NF-e (ambiente × 20 °C) | Conv. ICMS 110/07, cláusula nona, § 8º | volume "convertido a 20º C, quando emitida pelo produtor [...]"; "à temperatura ambiente, quando emitida pelo distribuidor de combustíveis ou pelo TRR" | CONFIRMADO |
| perdas e sobras informadas | Manual i-SIMP Distribuidores v1.3 | códigos 1021001 e 1022004, quantidades "considerando à temperatura de 20° Celsius e pressão de 1 (uma) atmosfera"; **sem limite de tolerância** | CONFIRMADO |
| boletim de conformidade | Res. 807/2020, arts. 9º e 10; Res. 828/2020, arts. 5º e 40, II | "O distribuidor [...] deverá analisar uma amostra representativa [...] e emitir o boletim de conformidade" · guarda de 12 meses | INFERIDO (cópia sem URL de origem; reconferir no in.gov.br) |
| rastreabilidade na NF-e | Res. 807/2020, art. 11; Res. 898/2022, art. 7º, § 3º | código ANP do produto e número do boletim no documento fiscal · "O número do envelope de segurança da amostra-testemunha deverá ser indicado [...] na documentação fiscal" | INFERIDO (cópia sem URL de origem; reconferir no in.gov.br) |
| certificado no recebimento | Res. 950/2023, art. 22, V | "solicitar ao fornecedor autorizado o certificado de qualidade [...] no ato de seu recebimento" | CONFIRMADO |
| recusa de produto fora da especificação | Res. 907/2022, art. 8º | distribuidor "obrigados a recusar o recebimento [...] caso constate qualquer não-conformidade" | CONFIRMADO |
| lacre do caminhão-tanque | Res. 898/2022, art. 2º e § 1º | compartimentos, bocais e válvulas "lacrados"; a obrigação de lacrar é de quem vende ao posto | INFERIDO (cópia sem URL de origem; reconferir no in.gov.br) |
| aferição do caminhão-tanque | Portaria INMETRO 49/2022, itens 2.2.1, 2.2.2 e 5.3.4 | volumes "referidos à temperatura de 20 °C" · "erro máximo admissível [...] 0,25 %" · validade de 2 anos | CONFIRMADO |
| calibração de medidor e bomba | Portaria INMETRO 227/2022, itens 3.1.1 e 3.1.2 | ±0,3% na verificação inicial; ±0,5% nas subsequentes | CONFIRMADO |
| documentos da carga perigosa | Res. ANTT 5.998/2022, art. 23 | CTPP/CIPP, CIV e o documento para o transporte de produtos perigosos | CONFIRMADO |

## 4. O que a norma não traz (não citar como exigência)

- **Validação de sistema, integridade de dados e trilha de auditoria:** não há exigência ao distribuidor (seção 1).
- **Tolerância de perda para a distribuidora:** não achada, nem na ANP nem no ICMS.
  - Os 0,6% são do posto (Res. 884/2022, art. 5º) e disparam investigação; não são "tolerância de evaporação".
  - A Receita (SC Cosit 223/2023) aceita perdas por evaporação de até 0,6% no custo. Marca INFERIDO: não há cópia local do texto para conferir, e a revisão adversarial de 28/09 não o verificou.
  - DESCONHECIDO para distribuidor.
- **Guarda por 5 anos:** vale para o TRR (Res. 938/2023) e para a legislação fiscal. Para o distribuidor, a ANP exige 6 meses.
- **Correção a 20 °C pela Res. Conjunta 1/2013:** incorreto. A base é a Res. 894/2022.
- **Res. 807/2020 como base de rastreabilidade de carregamento:** incorreto. A 807/2020 é a especificação da gasolina.

## 5. Pendências de fonte

1. Texto consolidado oficial da ANP (atosoficiais.com.br): confirmar as alterações da 950/2023.
2. Ato COTEPE vigente com os valores do FCV. O mais recente visto foi o 64/19. DESCONHECIDO.
3. Se o i-SIMP exige volume a 20 °C: a Res. 729/2018 não diz; o manual diz 20 °C para perdas e sobras.
4. Portaria INMETRO 291/2021: conferir numa página do INMETRO.
5. Reconferir no in.gov.br as cópias das Res. 884, 898 e 807, que foram lidas de arquivo baixado sem URL de origem registrada.

## 6. URLs (acesso em 28/09/2026)

- Res. 950/2023, DOU: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=515&pagina=94&data=09/10/2023&captchafield=firstAccess · consolidado (secundário): https://www.legisweb.com.br/legislacao/?id=469715
- Res. 729/2018, DOU: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=515&pagina=42&data=14/05/2018&captchafield=firstAccess
- Res. 868/2022 (página da ANP): https://www.gov.br/anp/pt-br/assuntos/dados-estoques-combustiveis
- Res. 894/2022: https://www.in.gov.br/web/dou/-/resolucao-anp-n-894-de-18-de-novembro-de-2022-445345667
- Res. 807/2020: https://www.in.gov.br/web/dou/-/resolucao-n-807-de-23-de-janeiro-de-2020-239635261
- Res. 968/2024: https://www.in.gov.br/web/dou/-/resolucao-anp-n-968-de-30-de-abril-de-2024-557405632
- Res. 907/2022: https://www.in.gov.br/web/dou/-/resolucao-anp-n-907-de-18-de-novembro-de-2022-445396653
- Res. 828/2020: https://www.in.gov.br/web/dou/-/resolucao-n-828-de-1-de-setembro-de-2020-275409699
- Res. 898/2022: https://www.in.gov.br/web/dou/-/resolucao-anp-n-898-de-18-de-novembro-de-2022-445345820
- Res. 884/2022: https://www.in.gov.br/web/dou/-/resolucao-anp-n-884-de-5-de-setembro-de-2022-427633674 · FAQ LMC: https://www.gov.br/anp/pt-br/acesso-a-informacao/perguntas-frequentes/agente-economico/livro-de-movimentacao-de-combustiveis
- Res. 950/2023 (DOU): https://www.in.gov.br/web/dou/-/resolucao-anp-n-950-de-5-de-outubro-de-2023-515392572
- Lei 9.847/1999: http://www.planalto.gov.br/ccivil_03/leis/l9847.htm · Lei 9.478/1997: http://www.planalto.gov.br/ccivil_03/leis/l9478.htm
- Manuais i-SIMP: https://csa.anp.gov.br/downloads/manuais-isimp/Manual-do-ISIMP-Geral-DPP.pdf · https://csa.anp.gov.br/downloads/manuais-sdl/Manual%20do%20i-SIMP%20-%20Distribuidores%20de%20Combust%C3%ADveis%20L%C3%ADquidos.pdf
- Conv. ICMS 110/07: https://www.confaz.fazenda.gov.br/legislacao/convenios/2007/CV110_07 · 15/23: https://www.confaz.fazenda.gov.br/legislacao/convenios/2023/CV015_23 · 199/22: https://www.confaz.fazenda.gov.br/legislacao/convenios/2022/CV199_22
- NT NF-e 2023.001: https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Li420kNzaH0%3D
- SC Cosit 223/2023: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=133749
- Res. ANTT 5.998/2022: https://anttlegis.antt.gov.br/action/ActionDatalegis.php?acao=detalharAto&tipo=RES&numeroAto=00005998&seqAto=000&valorAno=2022&orgao=DG%2FANTT%2FMI&codTipo=&desItem=&desItemFim=&cod_menu=5408&cod_modulo=161&pesquisa=true
- Portaria INMETRO 227/2022: https://www.in.gov.br/web/dou/-/portaria-n-227-de-26-de-maio-de-2022-403722830 · 49/2022: https://www.in.gov.br/web/dou/-/portaria-n-49-de-8-de-fevereiro-de-2022-379553356 · arqueação: https://www.gov.br/inmetro/pt-br/assuntos/metrologia-legal/controle-legal-de-instrumentos-de-medicao/modalidades/arqueacao-de-tanque · 291/2021 (secundário): https://www.legisweb.com.br/legislacao/?id=417192
- Res. Conjunta ANP/INMETRO 1/2013 (secundário): https://www.legisweb.com.br/legislacao/?id=255251
