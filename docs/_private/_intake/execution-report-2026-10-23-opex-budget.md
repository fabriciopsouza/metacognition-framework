# Execution-report — encerramento de bloco (ADR-038/052 · tier OWNER · privado, não distribuído)

Sessão 03c62e3b (21–23/10/2026): retomada de um projeto de OPEX, atualização dos relatórios por uma view de BI em vez
de consultas manuais ao ERP, orçamento base zero do ano seguinte e dash orçado × realizado; handoff para outra sessão.

- **Tokens:** NÃO MEDIDO — sem telemetria de token exposta ao agente (dependência do host; ver LIMITS.md)
- **Tempo (wall-clock):** ~3 dias de calendário, sessão interativa com interrupções (NÃO MEDIDO em horas)
- **Turnos:** NÃO MEDIDO
- **Arquivos tocados:** ~45 (3 repositórios privados: projeto, biblioteca de outra empresa, pesquisas) — contagem aproximada
- **Testes:** gates do gerador (G1–G4), canário de referências e guardas do pre-commit do projeto; validação cruzada
  1.170/1.170 (desembolso × view); R6 em 32 recortes (dash)
- **Rodadas de retrabalho:** 14 rodadas de QA adversarial isolado (Sonnet); 8 reprovações, todas corrigidas antes do commit

## Placar gate × achado (quem pegou o quê)
| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Entrada de mercadoria marcada "paga" (compensação GR/IR) no caixa do diretor | QA isolado | reconciliação view × export (só compara linhas, não semântica de compensação) |
| 39% do caixa compensado por documento intermediário (FB05/FBZ2), não por pagamento | autor, ao estender para 3 anos | nenhum: a regra "compensado = pago" vinha do bloco validado |
| Nota do ano anterior paga no ano corrente fora do caixa | autor | nenhum (filtro por exercício herdado) |
| Apropriação do SAC sem fornecedor (chave de 3 letras) ficou na sugestão | QA isolado | G3/G4 eram tautológicos |
| Palavra genérica ("SOFTWARE") casando fornecedor errado (−R$ 581 mil) | autor (revisão dos maiores) | nenhum |
| Gráfico de desvios pulava o 8º item (slice) | QA isolado | trava R6 da página somava a lista completa, não a exibida |
| Variável local `R` escondendo a função `R` (TDZ) | autor, pelo console do navegador headless | nenhum teste de navegador no pre-commit |
| Commit anunciado como feito, barrado pelo pre-commit | autor, dois blocos depois | exit code da cadeia `;` era do último comando |
| Referências relativas a outros repos quebrando o canário | canário de referências do projeto | — (funcionou) |
| Afirmação "merge feito" no handoff antes do merge | QA isolado | — |

## Detecção: framework × humano (quem pegou o quê — mecanismo vs. revisão humana)
- Mecanismo: canário de referências (2 commits barrados, correto); gates de reconciliação view × modelo (provaram a base).
- QA isolado (heterogêneo): a maioria dos defeitos de semântica e de UI.
- Humano (dono): apontou o defeito do drill no painel de referência e a necessidade das duas visões (competência e desembolso).

## Gaps (não-bloqueantes detectados — flagados, não silenciados)
- Fatura lançada direto no ativo fica fora do desembolso (declarado no README do projeto).
- Script de atualização (`atualiza.py`) escrito e não executado nem revisado: passado à próxima sessão como item 1.
- Pesquisa de aprendizes v1 com QA FAIL de classificação de fonte; v2 com o autor da pesquisa.

## Melhorias (do framework/processo — adição passa pela régua §0)
- Gate tautológico apareceu de novo (G3/G4 "fornecedores = linha"): o padrão "soma de partição exaustiva sempre fecha"
  já está na memória; vale virar item explícito do checklist do qa-critic para gerador de dados (sem código novo).
- Commit em segundo plano: conferir `git log` antes de anunciar (memória nova `commit-em-segundo-plano-conferir-log`).

## Boas práticas (o que funcionou — reutilizável)
- Provar a fonte nova contra o número oficial do cliente ao centavo antes de construir em cima (view × modelo do planejamento).
- Validação cruzada independente de um cálculo novo nos casos simples (1.170/1.170) antes de confiar nos complexos.
- Isolamento entre clientes: prints e números de um cliente ficam na biblioteca dele; o outro recebe só regras de formato.
- Página de dash com trava interna: se cartão ≠ tabela ≠ soma dos desvios, o título avisa em vez de mostrar número.
- Captura headless em 1366×768 e 1920×1080 a cada mudança de layout.

## Lições por skill (agnóstico de domínio — o que daqui serve a OUTRO projeto)
- dev: "compensado" no ERP não é "pago": seguir a cadeia de compensação até o documento de pagamento; nota parcelada
  paga em datas diferentes; nome curto e palavra genérica não identificam fornecedor sem lista de exclusão e apelido explícito.
- discovery: ao estender um relatório validado (1 ano → 3 anos), refazer as perguntas de definição (por exercício ou por data de pagamento?).
- architect: separar fonte única das consultas (um script) da documentação; extrair para arquivo temporário e só trocar quando todas as extrações passarem.
- qa-critic: pedir ao revisor que reproduza números em script próprio sem gravar; rodadas curtas focadas no que mudou.
- docops: handoff precisa afirmar só o que já é verdade no git; usar caminho absoluto em texto simples para arquivo de outro repo.
- research/spec/ux: fonte secundária nunca é CONFIRMADO; referência visual de outro cliente vira regra de formato com teste de aceite.
