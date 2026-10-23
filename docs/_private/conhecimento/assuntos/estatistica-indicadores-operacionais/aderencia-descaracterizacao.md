# Dados de demonstração: descaracterização com prova de aderência

## Transformação descaracterizante que preserva a conclusão das análises
- **Tipo:** runbook
- **Pergunta:** Como transformar dados reais de um cliente (volumes, totais, datas, códigos) para usá-los em demonstração ou POC, provando que as análises (correlação com defasagem, sazonalidade, Pareto, previsão) chegam à mesma conclusão que nos dados originais?
- **Fonte:** pesquisa de 23/10/2026 num repositório privado de cliente (script `fatores.py`, 18 análises, 30 sorteios, 3 controles negativos); o caminho fica no projeto do cliente, não aqui
- **Verificado em:** 23/10/2026
- **Confiança:** CONFIRMADO por execução (18 de 18 análises aprovadas em 30 de 30 sorteios; os 3 controles negativos reprovaram o que atacam); QA adversarial pendente
- **Classe:** conceito

Transformação (o que pode mudar):
1. Escala: todo volume, valor e total multiplicado por **um único fator secreto** (ex.: sorteado entre 0,2 e 5, nunca gravado). Fator por família ou por unidade é proibido: muda o mix e o Pareto (efeito de mix).
2. Ruído multiplicativo log-normal com σ ≤ 2% por registro; grupo com menos de 30 registros por período sai dos índices por grupo (senão o ruído domina).
3. Datas deslocadas só em múltiplos de 364 dias (mantém dia da semana e mês).
4. Códigos (cliente, unidade, evento, produto) por permutação aleatória; produto vira família.
5. Medida física (temperatura etc.): um deslocamento constante único para todas as séries da mesma grandeza; ruído ≤ 0,1.
6. Taxas: ruído aditivo ≤ 0,3 p.p., limitado ao intervalo válido.
7. Grupo com menos de 3 unidades suprimido; contagem de unidades publicada em faixa.

Prova:
1. Rodar as mesmas análises nos originais e nos transformados, em 30 sorteios independentes; aprovado = 30 de 30.
2. Critérios: participação ±1 p.p. e mesmos 3 primeiros; Pareto e Gini ±1 p.p.; índice mensal ±0,02 (total) e ±0,03 (grupo), mesmo mês de pico; CV ±10% relativo; dia da semana ±0,02; correlação com mesmo sinal quando |r| ≥ 0,1, ±0,05 por defasagem e mesma melhor defasagem; WAPE ± máx(1 p.p.; 10%) e mesmo melhor modelo; taxas ±2 p.p. (proporção) ou ±0,5 p.p. (pontualidade).
3. Controles negativos obrigatórios, que têm de reprovar: escala por família (reprova mix e Pareto), datas +10 dias (reprova índice mensal, dia da semana, previsão), ruído de 30% (reprova correlação e índices).
4. Publicar só fatores sem escala, arredondados.

Limites: aderência prova que a mesma lógica chega ao mesmo resultado, não que a lógica está certa; correlação perto de zero só reproduz "sem relação"; taxa não escalada passa por construção (o teste só confirma que o ruído é pequeno).
