# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

- **Sessão:** 15–16/09/2026 · **Blocos:** A (painel E2E + medidor de slide) · B (estrutura de pasta de projeto) · C (enforcement do framework) · D (distribuição pública)
- **Repos:** capacidade de apoio a projetos (externo ao núcleo) · `metacognition-framework`
- **Modelo:** autor **Opus**, QA adversarial **Sonnet isolado** (degrau abaixo, ADR-078)
- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)
- **Tempo (wall-clock):** NÃO MEDIDO
- **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** 70 staged no framework · 8 no repo de projetos
- **Testes:** 665 no repo de projetos (264 mutações) · 89 canários no framework
- **Rodadas de retrabalho:** 3 no bloco A (rodadas 3, 4 e 5 do QA; 2 FAIL antes do PASS) · 1 no bloco C (rodada 23, FAIL)

## Placar gate × achado (quem pegou o quê)

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| A-6: a janela de mesclagem era medida pelo dado que a corrupção já truncou | QA isolado (rodada 3) | a prova de mutação — não havia sabotagem pareada para mesclagem nas ÚLTIMAS linhas |
| Falso positivo de elipse: `.g-rot` acusado de corte, quebrando a ONE-PAGE | QA isolado (rodada 4) | **a própria doc**: `docs/ONE-PAGE.md` manda rodar `medir_slide.py` contra esse HTML, e ninguém rodou depois de mexer no medidor |
| Falso NEGATIVO: elipse sem `white-space:nowrap` suprimia corte real | QA isolado (rodada 5) | nenhum — régua nova, sem caso real no repo |
| M-20 nasceu com âncora órfã (`repr()` escapou a barra) | checagem de âncora obsoleta do `provar_mutacao.py` | o próprio `ast.parse`, que prova que o arquivo PARSEIA, não que a âncora CASA |
| Âncora ambígua (`R7`) acertava o alvo por ordem de aparição | QA isolado (rodada 5) | nenhum — virou mecanismo: o runner recusa âncora ambígua, e a achou na 1ª execução |
| Seis números da vitrine mantidos à mão | `export-clean.py` (falhava) | falhava certo, mas **eu diagnostiquei errado** (88/86); o QA mediu e eram 89/87, e a varredura achou 85 no pacote final |
| Arquivos de DADOS de `tools/` fora da matriz de papéis | QA isolado (rodada 23) | o canário da classe — que guardava a classe pelos casos lembrados, não pela pasta |
| Canário órfão (`test_export_so_rastreados.py`) sem registro | `test_capabilities.py` | **funcionou** — gate pegou sem ajuda |
| Deleção do `execution-report.md` quebrava o `consistency_gate` | QA isolado (rodada 23) | o próprio `consistency_gate`, que não roda no pre-commit |

## Detecção: framework × humano (mecanismo vs. revisão)

- **Mecanismo pegou sozinho (3):** âncora órfã, canário órfão, gate de nomes.
- **QA adversarial pegou (6):** os quatro achados de calibragem do medidor e do painel, a 4ª instância do "interruptor fora da matriz", e a âncora ambígua.
- **Nenhum foi pego por revisão humana do dono** nesta sessão — o dono corrigiu *processo*, não código: mandou verificar o `4.` nas outras pastas (e era `Execução`, não `Testes`), e apontou que perguntar se o QA é obrigatório já é o erro.

## Gaps (não-bloqueantes, flagados e não silenciados)

- `-webkit-line-clamp` (elipse vertical) ainda é acusado como corte. Nenhum gerador de página usa hoje; débito registrado.
- `provar_mutacao.py` roda só o teste PAREADO por sabotagem, não a suíte inteira.
- Canário anti-vazamento do `RATE-CARD.example.md`: tabela e prosa estão cobertas (`R$`, `reais`, `dólares`, `US$`, `BRL/USD/EUR`, `/h`, `/dia`, `/semana`, `/mês`, `/ano`). **Segue escapando, declarado:** número por extenso ("trezentos reais") e taxa sem marcador de moeda ("2.400 por dia"). Medido contra sete frases; separador de milhar **não** é escape — "1.500,00 reais" já é capturado pela palavra que o ancora.
- `3. Cronogramas` recebe a pasta e não o conteúdo: o modelo de cronograma chegou em 17/09 e ainda não foi incorporado. Medido: 18 das 50 pastas `3. Cronogramas` da biblioteca têm conteúdo, e o formato da casa é Gantt semanal.
- Sem snapshot/tendência entre execuções; `.pptx` não é gerado a partir dos mesmos dados.
- **Nenhum gate lê ESTE arquivo.** O canário de procedência narrativa varre a vitrine pública e o prompt web, nunca o execution-report interno — e a versão anterior desta mesma linha descrevia como aberto um gap que fora fechado na mesma rodada. Só um crítico lendo pegou. Enquanto não houver canário aqui, toda afirmação deste relatório vale o que vale a revisão humana dela.

## Melhorias do framework/processo (régua §0 — funde ou remove ≥ adiciona)

1. **A vitrine passou a ser gerada.** Os seis números de `#provas` saem de `--corrigir`, na mesma medição que o gate confere, e o `export-clean.py` a roda **duas vezes** — no passo 6 e depois do tier podar (8-bis), porque a árvore do passo 6 ainda encolhe. Quatro árvores, quatro números corretos: dev 89, premium 87, public e nonadmin 85.
2. **A frase por extenso perdeu o dicionário digitado à mão.** `por_extenso()` escreve a frase E constrói o mapa que o gate usa para reconhecê-la — e isso expôs que a conferência era por substring (`cinquenta e nove` contém `cinquenta` e `nove`). Passou a ser por palavra inteira, casamento mais longo.
3. **Matriz de papéis por PASTA, não por arquivo lembrado.** `prefix: tools/` cobre os 8 arquivos de dados que parametrizam gates — o QA achou 2. É a lição da 20ª rodada aplicada: `exact` cobre só o que alguém listou, e o irmão ao lado passa.
4. **O runner de mutação recusa âncora ambígua**, fail-closed, com a instrução de como desambiguar.
5. **`medir_slide.py` saiu de zero testes para 16**, e o comportamento do JS passou a ser provado RENDERIZANDO — presença de string no fonte não prova comportamento.

## Classe de defeito que mais se repetiu (e o que ela ensina)

**A asserção olha o mesmo fato que a sabotagem preserva.** `assert "overflowY" in MEDIDOR` continua verde com a condição envolvida em `false && (...)`. Três ocorrências nesta sessão. Os dois asserts decorativos foram **removidos**, não reescritos: a proteção real já estava nos testes que renderizam.

Segunda em frequência: **medir a caixa antes de ela ser a caixa final.** O medidor de slide media o `.slide` enquanto um `.cartao` engolia o excesso; o gate da vitrine media a árvore de export enquanto o tier ainda ia podar. Mesmo defeito, dois domínios, no mesmo dia.
