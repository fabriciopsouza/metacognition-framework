---
name: service-valuation
version: 1.1.0
source: ADR-114 (2026-08-30) — método trazido de fora e calibrado pelo caso H-01, em que a v1.0 errou o preço em uma ordem de grandeza (R$ 270.000 -> R$ 13.000)
last_review: 2026-08-30
description: >-
  Valoração sênior de qualquer serviço técnico ou consultoria, entregue ou a entregar, pelo VALOR
  ENTREGUE e pelo preço de mercado, não apenas pelas horas trabalhadas. Agnóstica de disciplina:
  SAP e ERP, SAC, Power BI, Tableau, Python, dados, automações e RPA, integrações, IA e LLM,
  cloud, treinamento, consultoria de processo. Use para "quanto vale isso", "quanto eu cobraria
  por esse trabalho", "faça a estimativa de custo desse desenvolvimento", "essa proposta está
  cara?", "monta a memória de cálculo dessa entrega", "quanto custaria isso no mercado". Também
  dispara quando existe entrega feita sem proposta formal e é preciso demonstrar valor de forma
  auditável. Produz sempre memória de cálculo rastreável, com cada número classificado por origem
  e confiança. NÃO use para: orçamento de licença ou material sem serviço, produto de prateleira,
  ou horas já contratadas a taxa fechada, que é aritmética.
---

# Valoração de serviço: preço por valor entregue, com memória de cálculo

Método transversal. A disciplina do trabalho (SAP, SAC, Python, automação, o que for) é
**configuração**, não regra: entra pelo arquivo `RATE-CARD.md` no Passo 0 e não altera
nenhum passo do método. **Onde esse arquivo mora, e em que ordem procurá-lo, está no §12** — no
núcleo ele não fica ao lado desta skill.

## 1. Regras que não cedem

1. **Não fabricar número.** Toda cifra recebe origem e classificação. Sem origem, o número
   não entra. Se faltar dado essencial, escreva `[DESCONHECIDO]` e siga com a faixa aberta.
   Nunca preencher lacuna com estimativa apresentada como fato.
2. **Classificação obrigatória em duas dimensões**, por linha:
   `[CONFIRMADO | INFERIDO | DESCONHECIDO]` (origem) e `[ALTA | MÉDIA | BAIXA]` (confiança).
3. **Rastreabilidade por ID**, referenciada nas fórmulas: `E-nn` evidência, `P-nn` premissa,
   `F-nn` fase de esforço, `T-nn` taxa, `V-nn` componente de valor, `C-nn` cálculo,
   `R-nn` risco.
4. **Entrega em arquivo** versionável, não resposta de chat. Mínimo `MEMORIA-CALCULO.md`.
5. **Faixa antes de ponto.** Sempre mínimo / provável / máximo.
6. **Teto de valor manda no preço.** Preço acima do valor que a entrega gera é preço errado,
   mesmo com horas que o justifiquem. Teto abaixo do piso significa que o serviço não se
   paga como desenhado: parar e dizer isso.
7. **Retrabalho do fornecedor não é entrega.** Esforço gasto corrigindo defeito
   introduzido por quem executa — regressão, retrabalho por erro de leitura de requisito,
   conserto de conserto — sai do esforço faturável. Só entra o que o cliente teria pagado se
   a entrega tivesse saído certa da primeira vez. Identificar pelos commits de correção, pelos
   achados de revisão e pelo registro de defeitos. Declarar quanto foi excluído.
8. **Faixa de unidade é TRAVA, não sugestão.** Se o esforço bottom-up (Passo 2) sair do
   intervalo da unidade de entrega da disciplina (`RATE-CARD.md` seção 4), **o bottom-up é o
   suspeito**, não a faixa. Refazer o Passo 2 ou escrever, com evidência, por que este caso é
   exceção. Estourar o topo da faixa sem essa justificativa invalida a valoração.
9. **Sem fonte independente, a Lente B não existe.** É proibido usar o Piso como Referência.
   Quando não houver nenhuma das fontes 1 a 4 do Passo 4, a Lente B é `[DESCONHECIDO]` e a
   triangulação perde uma perna — o resultado passa a ser **faixa**, nunca ponto, e isso vai
   escrito na primeira linha da entrega.
10. **Teto indeterminado não autoriza preço.** Sem `Teto`, não há "preço provável": há custo
   de reconstrução e uma decisão do cliente. Ver a quarta linha da tabela do Passo 7.
11. **Teste do espanto.** Antes de entregar: se um profissional do mercado cobraria uma ordem
   de grandeza menos por este resultado, a diferença tem de estar explicada em UMA frase que o
   cliente aceite. Se não estiver, o número está errado — não o cliente.
12. **Histórico próprio vence rate card.** Se existir `HISTORICO-ENTREGAS.md` — **onde e em
   que ordem procurá-lo está no §12**, como a Regra 8 aponta a seção 4 do `RATE-CARD.md` — com
   entregas anteriores e horas reais, ele é `[CONFIRMADO]` e substitui qualquer faixa default.
   Ler antes de estimar.

## 2. Passo 0 — Classificar a demanda

Oito eixos. O primeiro seleciona o perfil de taxa e as unidades de comparação; os demais
alimentam multiplicadores e modelo de cobrança.

| Eixo | Opções |
|---|---|
| **Disciplina** | ERP funcional · ERP técnico · Analytics/BI · Engenharia de dados · Automação/RPA · Integração/API · IA/ML/LLM · Cloud/infra · Qualidade e validação · Gestão/PMO · Treinamento · Consultoria de processo/negócio |
| Natureza | correção de defeito · evolução · configuração/parametrização · implantação · análise/diagnóstico · automação de processo · produto de dado · arquitetura · capacitação |
| Tipo de suporte necessário | AMS por chamado · bolsa de horas · projeto com escopo fechado · body shop · consultoria pontual · plantão/on-call · garantia pós-entrega · sustentação da própria entrega · transferência de conhecimento |
| Criticidade | cosmética · operacional · financeira · fiscal/regulatória · parada de produção · decisão executiva baseada no número |
| Ambiente | não regulado · regulado — **o projeto declara qual norma** (ADR-010) · missão crítica 24x7 |
| Escassez do conhecimento | commodity · especializado · raro no mercado |
| Reversibilidade | reversível · irreversível · afeta dado histórico ou obrigação acessória |
| Recorrência do benefício | pontual · recorrente mensal · recorrente anual · permanente |

Cada eixo vira uma linha `P-nn` com justificativa de uma frase. Eixo não determinado vira
`[DESCONHECIDO]` e entra na lista de perguntas do final.

## 3. Passo 1 — Inventário de evidência

Listar o que existe de fato, antes de estimar. Onde procurar varia com a disciplina, o
princípio não varia:

- artefatos entregues: programa, transação, modelo, história de SAC, dashboard, medida,
  fluxo, robô, script, notebook, pipeline, endpoint, prompt, playbook, material de aula;
- commits, arquivos criados ou alterados, branches, pull requests;
- documentos: análise, especificação, protocolo de teste, dicionário de dados, manual;
- tickets, e-mails e threads que estabelecem o problema e desde quando ele existe;
- ambientes tocados (DEV, QAS, PRD, workspace, tenant) e evidência de homologação;
- volume real processado: registros, usuários, execuções por mês, tempo de ciclo.

Cada item vira `E-nn` com origem literal (caminho, hash, número do chamado, data).
**Só evidência pode ser `[CONFIRMADO]`.** Esforço reconstruído a partir dela é sempre
`[INFERIDO]`.

Contagem de linhas de código, número de páginas de dashboard ou quantidade de passos de um
fluxo servem como evidência de **escopo**, nunca como proxy de valor **nem como âncora de
esforço**. Duas razões: densidade de comentário e de teste varia por ordem de grandeza entre
projetos, e código gerado com assistência de IA desacopla linha de hora. Ancore esforço na
unidade de entrega da disciplina e no número de decisões que tiveram de ser tomadas. Automação de dez linhas
que elimina conferência manual diária vale mais que relatório de mil linhas que ninguém abre.

## 4. Passo 2 — Esforço reconstruído por fase

Fases padrão, agnósticas. Omitir as que não ocorreram, nunca inventar as que não ocorreram.

`F-01` Entendimento e diagnóstico · `F-02` Levantamento com áreas · `F-03` Especificação ·
`F-04` Construção · `F-05` Teste unitário · `F-06` Teste integrado · `F-07` Peer review ·
`F-08` Documentação · `F-09` Homologação com usuário · `F-10` Publicação e atividades em
produção · `F-11` Garantia/hypercare · `F-12` Gestão e governança.

O que conta como `F-04` Construção, por disciplina:

| Disciplina | Construção é |
|---|---|
| ERP funcional | customizing, dados mestre, teste de configuração |
| ERP técnico | código, enhancement, formulário, interface |
| Analytics/BI | modelo semântico, medidas, visual, publicação, segurança de linha |
| Engenharia de dados | ingestão, transformação, qualidade, orquestração |
| Automação/RPA | fluxo, conectores, tratamento de exceção, agendamento |
| Integração/API | contrato, mapeamento, autenticação, reprocessamento |
| IA/ML/LLM | preparação de dado, treino ou prompt, avaliação, guarda-corpos |
| Consultoria de processo | mapeamento, desenho to-be, matriz de responsabilidade |
| Treinamento | roteiro, material, ambiente de prática |

Três regras de calibração:

- **Excluir o retrabalho do fornecedor.** Ver regra 7. Numa entrega com controle de versão,
  isso é mensurável: commits de `fix` que corrigem defeito próprio, achados de revisão
  interna, e a fase de garantia consumida por regressão. Registrar a linha
  `F-nn (excluído: retrabalho)` com o volume tirado, para o cliente ver que foi tirado.

- **Desconto de diagnóstico.** Se o cliente entregou a causa raiz pronta, `F-01` cai para o
  tempo de leitura e validação. Cobrar diagnóstico que não foi feito é o furo mais comum em
  estimativa de fornecedor.
- **Fase estrutural não é gordura.** Peer review, documentação, validação em ambiente
  regulado e publicação entram mesmo quando a construção é trivial.

## 5. Passo 3 — Lente A: custo (define o PISO)

```
Custo_base   = Σ ( horas_F-nn × taxa_perfil_T-nn )
Piso         = Custo_base × (1 + contingência) × (1 + despesas)
```

Contingência default 15%. Despesas default 8% com presencial, 0% remoto. Ambas são premissas
`P-nn` editáveis, nunca constantes escondidas em fórmula.

## 6. Passo 4 — Lente B: mercado comparável (define a REFERÊNCIA)

Ordem de preferência das fontes:

1. entrega própria anterior equivalente, com horas reais (`HISTORICO-ENTREGAS.md`) — `[CONFIRMADO]`
2. proposta real recebida para escopo equivalente — `[CONFIRMADO]`
3. contrato ou ata vigente com taxa por perfil — `[CONFIRMADO]`
4. rate card publicado do fornecedor ou do setor — `[CONFIRMADO]`
5. derivação a partir de salário de mercado do perfil — `[INFERIDO]`

Derivação da fonte 5:

```
Custo_hora_interno = salário_mensal × (1 + encargos) ÷ horas_mês_úteis
Taxa_faturada      = Custo_hora_interno × markup
```

Encargos default 75% para CLT no Brasil, 168 horas úteis por mês. Markups e faixas por
disciplina estão em `RATE-CARD.md`.

Comparar também pela **unidade de entrega da disciplina**, não só pela hora: por objeto
técnico, por dashboard, por fluxo automatizado, por pipeline, por integração, por turma de
treinamento. As faixas estão no rate card e são `[INFERIDO / BAIXA]` até serem calibradas com
histórico próprio.

**Declarar quando não existir referência pública.** Ausência de fonte é informação, não
licença para inventar precisão. E, sem fonte, a Lente B fica `[DESCONHECIDO]` — usar o Piso
como Referência é proibido pela regra 9.

**A pergunta que fecha a Lente B, e que quase sempre é esquecida:** *quanto custaria comprar
este RESULTADO pronto?* Não a hora — o resultado. Integrador de RPA com conector do ERP,
produto de prateleira, plataforma de automação com licença mensal, ou o custo de simplesmente
não fazer e manter o processo manual. Essa é a alternativa real do cliente, e é contra ela que
o preço é julgado — não contra a soma das horas de quem executa.

## 7. Passo 5 — Lente C: valor entregue (define o TETO)

Quantificar apenas o que houver evidência para sustentar. O resto fica `[DESCONHECIDO]` e
vira pergunta, não zero.

| ID | Componente | Como calcular |
|---|---|---|
| V-01 | Custo evitado | multa, autuação, retrabalho, perda de lote, parada, glosa, incidente. Valor × probabilidade × frequência anual |
| V-02 | Ganho operacional recorrente | horas/mês economizadas × custo-hora interno × 12 |
| V-03 | Receita destravada | volume adicional × margem, somente com número vindo do negócio |
| V-04 | Custo de reposição | o que custaria comprar a mesma entrega hoje, incluindo rampa de um terceiro |
| V-05 | Risco transferido | quanto vale o fornecedor assumir preço fechado, prazo ou garantia |
| V-06 | Valor de opção | reuso em outros processos, plantas, áreas ou clientes |
| V-07 | Qualidade de decisão | erro de decisão evitado por dado correto. Só com caso concreto documentado |
| V-08 | Velocidade | valor de antecipar o benefício em N meses = benefício mensal × N |

```
Valor_anual = Σ V-nn
Teto        = Valor_anual × taxa_de_captura
```

Captura default 5% a 15% do benefício do primeiro ano. Use 5% quando o cliente assume o
risco de execução, 15% quando o fornecedor assume.

Se `Valor_anual` for inteiramente `[DESCONHECIDO]`, dizer isso na primeira linha do resultado
e entregar apenas as lentes A e B, sinalizando que o preço está defendido por custo, não por
valor. Não estimar benefício sem base.

## 8. Passo 6 — Multiplicadores de contexto

Sobre o Piso, cumulativos, cada um registrado como `P-nn` com justificativa escrita:

| Fator | Faixa | Quando |
|---|---|---|
| Ambiente regulado | 1,15 a 1,40 | exige dossiê, rastreabilidade, controle de mudança |
| Criticidade fiscal, parada ou decisão executiva | 1,10 a 1,30 | erro gera perda direta ou obrigação acessória |
| Escassez de conhecimento | 1,10 a 1,50 | poucos fornecedores capazes |
| Urgência imposta | 1,15 a 1,35 | prazo abaixo do natural do escopo |
| Preço fechado com escopo aberto | 1,20 a 1,40 | fornecedor absorve variação |
| Sustentação da própria entrega inclusa | 1,10 a 1,25 | garantia estendida além do padrão |
| Reuso já pago em entrega anterior | 0,60 a 0,85 | reduz, não aumenta |

Multiplicador sem justificativa escrita não entra no cálculo. O mesmo efeito não pode ser
contado duas vezes com nomes diferentes.

**Teto do produto: 1,50.** Acima disso, exige aprovação escrita de quem vende, no próprio
documento, com o motivo. **Quatro fatores no PISO das faixas desta tabela chegam a 1,75** — já
estouram o teto sem que ninguém tenha decidido aumentar nada. Empilhar é o jeito mais fácil de
dobrar um preço sem nenhuma linha nova de evidência. (No caso `H-01` o produto foi 1,82, com
cinco fatores; com quatro, 1,75 é o máximo que esta tabela produz.)

**Escassez exige FONTE, não justificativa.** Nomear dois fornecedores que fariam o serviço, ou
mostrar busca sem resultado. "É raro" sem isso é opinião do vendedor sobre o próprio trabalho.

**Reversibilidade é de negócio, não de log.** Registro de auditoria que não se apaga NÃO torna
a operação irreversível: a pergunta é se o efeito no processo pode ser desfeito e a que custo.
Senha trocada por engano se corrige com outra troca; lançamento fiscal transmitido, não.

## 9. Passo 7 — Triangulação

```
Preço_provável = mediana(Piso, Referência, Teto), limitada ao intervalo [Piso, Teto]
```

| Situação | Conduta |
|---|---|
| Teto > Referência > Piso | caso saudável: recomendar o ponto provável e explicitar a margem entre Piso e Teto |
| Teto entre Piso e Referência | o mercado cobra mais do que a entrega vale aqui: recomendar o Teto e tratar a diferença como escopo a cortar, não desconto |
| Teto < Piso | parar. Entregar a conclusão e três alternativas: reduzir escopo, mudar o modelo de suporte, ou não fazer |
| **Teto indeterminado** | **não existe preço provável.** Entregar: (a) o custo de reconstrução, (b) a faixa de mercado do resultado equivalente, (c) as perguntas que fechariam o teto — e dizer que a decisão de preço depende delas. Multiplicar o piso e chamar de preço é o erro mais comum aqui |

## 10. Passo 8 — Revisão adversarial

Hipótese default: existe um furo.

- [ ] Fase cobrada sem evidência de que ocorreu?
- [ ] Diagnóstico entregue pronto pelo cliente e mesmo assim precificado cheio?
- [ ] O escopo técnico cobre todos os cenários descritos na evidência, ou só um deles?
- [ ] Fase com zero horas que na prática vai acontecer (gestão, publicação, garantia)?
- [ ] O mesmo benefício aparece em dois componentes `V-nn`?
- [ ] Multiplicador aplicado duas vezes com nomes diferentes?
- [ ] A taxa corresponde à disciplina e ao modelo de suporte declarados no Passo 0?
- [ ] Ganho recorrente anualizado sem projetar perpetuidade?
- [ ] Volume ou frequência usados no `V-02` vieram de evidência ou de suposição?
- [ ] Algum `[INFERIDO]` apresentado com precisão de `[CONFIRMADO]`?
- [ ] **Teste do espanto**: um profissional do mercado cobraria uma ordem de grandeza menos?
      Se sim, a diferença está explicada numa frase que o cliente aceite?
- [ ] Esforço de RETRABALHO do fornecedor foi excluído, e o volume excluído está declarado?
- [ ] O bottom-up cabe na faixa de unidade da disciplina? Se estourou, há justificativa escrita?
- [ ] A Referência tem fonte INDEPENDENTE, ou é o Piso disfarçado?
- [ ] Linha de código, página ou passo foi usada como âncora de esforço em algum lugar?
- [ ] O produto dos multiplicadores passou de 1,50? Há aprovação escrita?
- [ ] "Escassez" tem fonte, ou é opinião do vendedor sobre o próprio trabalho?
- [ ] "Irreversível" é do processo, ou só do log de auditoria?
- [ ] Um terceiro refaz a conta sem me perguntar nada?

Bater o número esperado não valida a conta. Verificar a semântica de cada linha, não só a
aritmética. Aprovar algo bem formatado e errado é falha.

## 11. Passo 9 — Entrega

Sempre `MEMORIA-CALCULO.md` no formato de `TEMPLATE-MEMORIA-CALCULO.md`, versionado.

Com mais de 8 linhas de esforço, mais de um cenário, ou necessidade de o destinatário
simular: planilha com abas `Premissas`, `Evidencias`, `Esforco`, `Valor`, `Cenarios`, taxas
como células de entrada e custos como fórmulas que as referenciam.

Ao final, alimentar `HISTORICO-ENTREGAS.md` — **o mesmo que você resolveu no §12, não um novo ao
lado desta skill** — com disciplina, escopo, horas reais e preço praticado. É o que transforma
faixa `[INFERIDO]` em base `[CONFIRMADO]` na próxima vez. Sem contrato assinado, registrar
mesmo assim com preço "não praticado": o caso `H-01` é exatamente isso, e é dele que saem as
quatro lições que hoje travam o método.

Fechar a resposta com no máximo cinco linhas: preço provável, faixa, lente dominante, maior
risco, próxima decisão.

## 12. Configuração de domínio — e onde ela mora

A skill descreve o **método**; o `RATE-CARD.md` descreve o **mercado** e o
`HISTORICO-ENTREGAS.md` descreve **as suas entregas**. Faixa de preço muda no rate card, nunca
aqui. Passo do método muda aqui, nunca no rate card.

**Eles não ficam ao lado desta skill, e a razão é de vazamento, não de gosto.** Este arquivo vive
no núcleo (`_shared/`), que é exportado para os pacotes públicos e para os repositórios-sombra
(`tools/web_export.py`). Taxa real e histórico de cliente num arquivo exportado é dado privado
publicado sem ninguém decidir isso.

**Ordem de resolução no Passo 0 — a primeira que existir ganha:**

| ordem | onde | quando é esta |
|---|---|---|
| 1 | `.claude/skills/service-valuation/RATE-CARD.md` no projeto em que você está | o projeto tem mercado próprio (ADR-010: o projeto declara o escopo) |
| 2 | `docs/_private/service-valuation/RATE-CARD.md` no repositório do framework | é o rate card do dono, versionado e fora do export |
| 3 | `exemplos/service-valuation/RATE-CARD.example.md` | só a estrutura, **sem número**: serve para criar o seu, nunca para precificar |

O mesmo vale para `HISTORICO-ENTREGAS.md`. **Declare no documento entregue qual dos três você
usou** — precificar com o exemplo e não dizer é apresentar estrutura vazia como se fosse mercado.

Se nenhum existir, o Passo 0 não tem taxa: as linhas `T-nn` nascem `[DESCONHECIDO]`, a Lente A
não fecha, e a entrega é faixa aberta com as perguntas — não um preço.

## 13. O que esta skill não faz

Não decide se o serviço deve ser contratado, não substitui parecer jurídico ou fiscal sobre
multa e obrigação acessória, e não estima benefício de negócio sem número fornecido pela
área. Nesses pontos, entrega a pergunta, não a resposta.
