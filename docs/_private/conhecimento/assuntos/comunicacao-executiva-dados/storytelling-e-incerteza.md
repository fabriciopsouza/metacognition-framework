# Storytelling com dados, mensagem executiva e incerteza — regras reutilizáveis

## regras de mensagem executiva com dados
- **Tipo:** pesquisa
- **Pergunta:** Como transformar indicadores em uma mensagem que um gestor superior entende em 2 minutos, sem exagero nem jargão?
- **Classe:** conceito
- **Fonte:** Minto (https://www.barbaraminto.com/); AR 25-50 §1-38, 2020 (https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN42124-AR_25-50-007-WEB-13.pdf); Duarte, HBR 2012 (https://www.duarte.com/blog/how-to-effectively-present-to-senior-executives/); Segel e Heer, IEEE TVCG 2010 (https://idl.cs.washington.edu/files/2010-Narrative-InfoVis.pdf); Cowan, BBS 2001 (https://philpapers.org/rec/COWTMN); carta aos acionistas de 2017 sobre memorandos narrativos de seis páginas; todos acessados em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** INFERIDO
- Ordem da fala: resposta com comparação + anúncio do pedido → contexto como fato, sem justificar → dado desfavorável sem atenuante e a ação em curso → pedido detalhado (até 3) → anexo.
- Até 3 mensagens (a memória de trabalho guarda cerca de 4 blocos); 5 a 10 minutos de condução e o resto em perguntas; regra de 10% (50 slides de anexo → 5 de resumo).
- Reunião em taça de martíni: trecho guiado e depois perguntas. Uma página escrita fica com o decisor.
- Título-conclusão só quando o teste sustenta; sem teste, título descritivo honesto.

## escala de frases para incerteza estatística
- **Tipo:** pesquisa
- **Pergunta:** Como dizer a um leigo que uma diferença não é estatisticamente firme sem afirmar que nada mudou?
- **Classe:** conceito
- **Fonte:** Altman e Bland, BMJ 1995 (https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html); Amrhein et al., Nature 2019 (https://pubmed.ncbi.nlm.nih.gov/30894741/); van der Bles et al., PNAS 2020 (https://ui.adsabs.harvard.edu/abs/2020PNAS..117.7672V/abstract); Padilla, Kay e Hullman, 2021 (https://friendly.github.io/6135/papers/Uncertainty_Visualization_Padilla_Kay_Hullman_2020.pdf); Gigerenzer et al., PSPI 2007 (https://pubmed.ncbi.nlm.nih.gov/26161749/); todos acessados em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** INFERIDO
- Diferença firme: "caiu/subiu de X para Y (diferença firme)".
- Intervalo estreito, dentro de uma margem definida como irrelevante: "estável".
- Intervalo largo que cruza zero: "sem mudança detectável; inconclusivo", com a faixa numérica (o número custa pouca confiança; a ressalva vaga custa mais).
- Amostra abaixo do mínimo: "poucos casos para medir".
- Diferença de percentuais em p.p., com o número absoluto ao lado; percentis e taxas em frequência ("9 em cada 10").
- Faixa sombreada com rótulo em frequência, porque o limite visual vira categoria para o leitor.

## linguagem de causa e atribuição em relatório gerencial
- **Tipo:** pesquisa
- **Pergunta:** Como relatar coincidências entre indicadores sem afirmar causa e sem culpar pessoas?
- **Classe:** conceito
- **Fonte:** Sumner et al., BMJ 2014;349:g7015; Hernán, AJPH 2018 (https://ajph.aphapublications.org/doi/10.2105/AJPH.2018.304337); "Postmortem Culture" (https://sre.google/sre-book/postmortem-culture/); Ross 1977, por resumo secundário (https://www.simplypsychology.org/fundamental-attribution.html); Deming, Out of the Crisis p. 315, por coletânea (http://management.curiouscatblog.net/2013/04/24/94-belongs-to-the-system/); todos acessados em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** INFERIDO
- "Coincide com" só vale acompanhado da hipótese explícita e do que a confirmaria; sem isso, o leitor completa a causa sozinho.
- O sujeito da frase é o indicador, não a pessoa; agregação por função, sem ranking individual.
- Identidade aritmética ("com P% menos pessoas, a demanda por pessoa subiu Q%") é dita como aritmética, sem "por isso".

## narrativa automática em painéis (padrões de mercado)
- **Tipo:** pesquisa
- **Pergunta:** Como os produtos de BI geram texto automático a partir de indicadores, e com que controles?
- **Classe:** retrato
- **Fonte:** Microsoft Learn, Narrative visual Custom, ms.date 25/09/2026 (https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-smart-narrative) e Copilot, ms.date 11/05/2026 (https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-create-narrative); Tableau Help, Pulse insight types (https://help.tableau.com/current/online/en-us/pulse_insights_platform_insight_types.htm); Tableau Exchange, Arria (https://exchange.tableau.com/en-us/products/47); todos acessados em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** CONFIRMADO por documentação dos fornecedores (retrato de 11/10/2026)
- Power BI Custom: até 4 resumos por visual e 16 por página; valores dinâmicos; sem achado, sem resumo.
- Power BI Copilot: o autor deve conferir o resumo; notas de rodapé ligam a frase ao visual; atualização manual depois de filtrar.
- Tableau Pulse: 14 tipos de achado, ligáveis por métrica, sobre modelos estatísticos determinísticos.
- Padrão comum (INFERIDO, síntese das documentações acima, não afirmação delas): estatística determinística primeiro, texto depois; cada frase rastreável até o visual; revisão humana no texto de IA.
