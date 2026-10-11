# Métodos estatísticos para painéis de indicadores operacionais — regras reutilizáveis

## "estável" por limites naturais, por recorte
- **Tipo:** pesquisa
- **Pergunta:** Como dizer que um indicador está "estável" com base estatística, separado por recorte, sem percentual fixo?
- **Classe:** conceito
- **Fonte:** Wheeler (https://www.spcpress.com/pdf/DJW251.pdf); Lakens 2017 (https://pmc.ncbi.nlm.nih.gov/articles/PMC5502906/); simulações reproduzíveis da pesquisa de 11/10/2026; acesso em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** INFERIDO
- Margem de equivalência (TOST com intervalo de 90%) baseada na amplitude móvel quase nunca dá "estável" quando a oscilação é sobretudo amostral (ex.: SLA): 0,0% a 0,08% em simulação com 50 a 5.000 casos por período.
- Regra que funciona: série do recorte em períodos do mesmo tamanho, mínimo 6 pontos; "mudou" se o valor novo sai dos limites naturais da XmR ou dispara regra de sequência; senão "estável" = dentro da variação habitual (não "provado igual"); sem série, usar o intervalo de 95% e dizer "sem diferença detectável".
- Alarme falso do método completo (R1 = 1 ponto além de 3 sigma; R2 = 2 de 3 além de 2 sigma do mesmo lado; R3 = 7 do mesmo lado) num período novo: cerca de 3% com 12 pontos de base e 6,5% com 5 (simulação, série normal).
- Converter sigma entre tamanhos de período, supondo independência: média, mediana ou proporção ÷ √k; contagem × √k.

## alerta de tendência curta ("N períodos seguidos piorando")
- **Tipo:** pesquisa
- **Pergunta:** Quantos períodos seguidos no sentido ruim justificam um alerta sem excesso de alarme falso?
- **Classe:** conceito
- **Fonte:** cálculo e simulação (pesquisa de 11/10/2026); Helsel et al., USGS TM 4-A3, 2020, cap. 12 (https://doi.org/10.3133/tm4a3); NIST e-Handbook 6.3.2.4 (https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm); acesso em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** INFERIDO
- Sem mudança real, a chance de os últimos k passos irem no sentido ruim é 1/(k+1)! para fluxo independente (k = 3: 1/24) e 1/2^k para estoque que se comporta como passeio aleatório (k = 3: 1/8).
- Com 2 fluxos e 2 estoques e k = 3, há até cerca de 30% de chance de algum alerta falso por semana; com k = 4 nos fluxos e k = 5 nos estoques, até cerca de 8%. Os valores de estoque são teto: uma fila real que volta à média tem menos passos seguidos (valor real desconhecido até medir).
- Mann-Kendall supõe independência: serve para fluxo (2,9% de alarme falso com 8 pontos), não para estoque (cerca de 35%).
- EWMA (λ entre 0,2 e 0,3) é alternativa para deriva pequena e gradual.

## comparar proporções e contagens com amostra pequena
- **Tipo:** pesquisa
- **Pergunta:** Que teste e que intervalo usar para SLA e para variação % de contagens com amostra pequena?
- **Classe:** conceito
- **Fonte:** Campbell, Stat Med 2007 (https://pubmed.ncbi.nlm.nih.gov/17315184/); Newcombe, Stat Med 1998; Brown, Cai e DasGupta, Stat Sci 2001; Holm, Scand J Stat 1979; acesso em 11/10/2026
- **Verificado em:** 11/10/2026
- **Confiança:** INFERIDO
- Teste de duas proporções: qui-quadrado "N−1" quando a menor frequência esperada é ≥ 1; Fisher é conservador (alarme falso de 0,1% a 2,8% em simulação com SLA alto).
- Intervalo: Wilson para uma proporção; Newcombe (dois Wilson) para a diferença em p.p.
- Variação % de contagem: com +50% observado, o IC exato condicional vai de −37% a +273% em 10 → 15 e de +3% a +119% em 50 → 75; mostrar % só com as duas contagens ≥ 20 e chamar de firme só quando o intervalo exclui zero.
- Muitas comparações: com 20 testes sem efeito real, 64% de chance de pelo menos um falso; corrigir com Holm.
