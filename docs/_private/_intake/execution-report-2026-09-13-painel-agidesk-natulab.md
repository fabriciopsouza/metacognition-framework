# Execution report — 2026-09-13 — painel da skill de projetos Agidesk/Natulab

> Rota: **squad** (pmo → discovery → architect → developer → qa-critic → docops) + `high-stakes-gate`.
> Autor: Fable (5 agentes de pesquisa isolados) + Opus (implementação).
> QA: **Opus adversarial isolado, em primeiro plano** — duas rodadas, a primeira REPROVOU.
> Entrega: `natulab-agidesk-projetos` PR #1 **merged** (`785d1c9` → `a7cc467`).

## O que foi entregue

| Arquivo | O que faz |
|---|---|
| `ferramentas/situacao.py` | cascata estrita de 6 situações, derivada dos dados |
| `ferramentas/painel.py` | % por peso, itens que pedem ação, agregações, causa comum, saídas md/csv/json |
| `ferramentas/selecionar_pasta.py` | seletor com GUI; separa causas de falha; detecta cópia local que não sobe |
| `docs/PAINEL.md` | a norma, com os incidentes que a justificam |
| +3 arquivos de teste, `provar_mutacao.py`, `backlog.exemplo.json`, `README.md`, `PENDENTE-QA.md` | |

**Prova:** 172 testes (eram 73) · **39 mutações, todas PEGAS** (eram 12).

## Lições por skill

### discovery
- **Pesquisa em 5 frentes paralelas com agentes isolados funcionou** — cada uma voltou com path:linha e classificação de confiança. O custo foi ~1,1 M tokens de subagente; o retorno foi um mapa que nenhuma leitura minha teria produzido no mesmo tempo.
- **A régua §0 pagou três vezes:** o `backlog.json` já era a SSoT (não criar `tarefas.yml`), as 4 portas de entrada já existiam no discovery, e o padrão de seção bypassável já existia (`adotado: {usa, por_que}`). O QA ainda assim reprovou meu desenho por adição pura — eu ia criar uma **terceira** fonte de estado.
- **Buscar a ausência é achado:** "TAP não existe na casa" só valeu como informação porque a busca cobriu 28.161 + 1.756 nomes de arquivo. Ausência não medida não é ausência.

### architect
- **Um esquema mínimo gerou todas as saídas de prazo** — mas a conclusão "gera TODAS as saídas" era falsa e o próprio documento a refutava duas seções abaixo (6 de ~30 campos do status report são automáticos). O QA pegou. Lição: conclusão de título tem de sobreviver à medição do próprio texto.
- **Dois eixos separados valem mais que um enum grande:** situação (função dos dados) × alerta (julgamento humano, ortogonal). Tentar caber tudo num só campo foi o que produziu os 17 rótulos de "Situação" para 4 classes no checklist NEXUS.

### developer
- **Escrevi a ferramenta que denuncia `#DIV/0!` alheio e reproduzi o defeito de aritmética nela** — `executado + faltante = 99,9`, por arredondar os dois lados em separado. O QA mediu com quatro itens.
- **Campo declarado e não aplicado é pior que campo ausente:** o `profundidade` do seletor mentia na configuração e escondia justamente as bibliotecas do SharePoint. Removido; a profundidade vive no próprio glob.
- **Fail-closed tem de valer nos dois caminhos do mesmo dado:** `pct=50.9` truncava calado enquanto `pct="50.5"` levantava; `estimativa_min` negativa virava 0,01 enquanto `peso` negativo levantava.
- **Heredoc colapsa barra-invertida dupla** mesmo com delimitador entre aspas — quebrou 4 entradas do `provar_mutacao.py`. Já estava na memória; paguei de novo. **Payload com escape vai pela ferramenta de escrita, nunca pelo shell.**

### qa-critic
- **Teste tautológico é a armadilha mais convincente.** `assert situacao in TODAS` com 200 casos *parece* rigoroso e não prende nada — a função só devolve constantes de `TODAS`. O QA provou apagando o ramo "Sem data": seguia verde.
- **Teste que compara a saída com a própria constante** (`list(linhas[0].keys()) == painel.CAMPOS_CSV`) concorda com qualquer mutação da constante. Contrato externo se testa com literal.
- **Mutação que não acha o alvo NÃO conta como passou** — duas das minhas ficaram obsoletas após as correções, e o verificador as reportou como inválidas em vez de verdes. Esse comportamento é o que faz o número significar algo.
- **Âncora de mutação precisa ser única:** `if p["alertas_humanos"]:` existe em duas funções; sabotar a primeira mediria a função errada.
- **O QA achou o que 2 rodadas minhas não acharam** porque atacou por fora: rodou o CLI com destino inválido, com JSON quebrado, com `--hoje` mal formatado, e criou um `subst` para testar caminho equivalente.

### docops
- **A fronteira do que NÃO se faz foi escrita junto com o que se faz** — em `docs/PAINEL.md`, no corpo do commit e no PR. Deferido com a razão é informação; deferido em silêncio é dívida.

## Descobertas de infraestrutura (fora do escopo, mas urgentes)

1. **464 arquivos / 535,9 MB de documentação de projeto existem só na máquina do dono.** A pasta `Natulab Laboratorio S.A\Tecnologia da Informação - Documentos` **não está sincronizada** — confirmado no registro do OneDrive (`ScopeIdToMountPointPathCache` tem 2 raízes montadas e essa não é uma delas) e pela divergência de projetos (o servidor tem 15/16/17 que a cópia local não tem). O `sync_sharepoint.py` vem publicando numa pasta morta. Decisão do dono: seguir usando a pasta local e subir manualmente.
2. **O modelo de status report da gerente não é template** — 331 linhas, zero placeholders, `rowspan` fixos. O CSS é reaproveitável literalmente; o corpo tem de ser reconstruído. E existem **duas edições divergentes em 8+ pontos**, sem edição canônica declarada.
3. **O rate card que precificaria qualquer projeto não tem fonte** — 22 perfis, "Última revisão: preencher na primeira execução" nunca preenchida. Mas existe base real não usada: AMS a 164–235 R$/h confirmados no orçamento, e uma proposta de escopo fechado de R$ 44.000,61.

## Gaps declarados

- **A janela do seletor (Tk) não tem teste automatizado** — não roda no CI, e o `except Exception` largo do `main` engoliria um bug dela como "sem_gui". Declarado no docstring do próprio arquivo.
- **O QA não conseguiu verificar completude** ("o que foi feito atende ao pedido?") por não ter a lista de requisitos em mãos — revisou correção, não cobertura. Metade da régua do repo ficou em aberto nesta rodada.
- **As 5 inconsistências do deck APOEMA** foram reconferidas por mim no PDF, exceto a divergência "10 riscos Alto no slide × 8 na planilha embutida", que exigiria reabrir o `.pptx`.
