# Andamento — 24/09/2026 (bloco D): OPEX por área, e o vazio que não provava nada

> Execution-report de encerramento de bloco (ADR-038/052/062 · tier **OWNER** · privado,
> não distribuído). Domínio: `C:\Users\fabriciosouza\budget-ti-thanner`, branch
> `feat/areas-bloco-47-preenchimento`, PR #2 (não mergeado). **Não commitado neste repo**:
> a árvore do framework estava na branch de outra sessão (`docs/ritos-2026-09-24-c-mrp`),
> e trocar de branch ou commitar por cima dela violaria a regra de sessões simultâneas.

## Onde estamos, em uma linha

A consulta que decide cadastro × árvore para a área (blocos 47) está escrita e mede em R$.
Na auditoria de placeholders que o dono pediu, a prova de que o caixa de TI estava "limpo"
caiu: a consulta só conseguia enxergar 1 documento em 421.

## Métricas

| Métrica | Valor |
|---|---|
| Tokens | NÃO MEDIDO |
| Commits no domínio | 2 na branch (`a89655c` + o de nomes, R$ e 29c) |
| QA adversarial isolado (Sonnet, só leitura) | 2 rodadas: FAIL (1 ALTA) → PASS |
| Mudanças posteriores ao PASS, sem QA | 47a/47b/47d com R$, 47f, 29c, revisão de P02 — **1º item da retomada** |
| Guardas (`verifica.py`) | código 0 antes de cada commit; 1 reprovação, por referência quebrada após renomeação do dono, corrigida |

## De onde saímos → onde chegamos

1. **Bloco 47 (preenchimento de KHINR/VERAK/ABTEI/FUNC_AREA).** Escrito só com campos
   provados pelas sondagens 41/41b. A pergunta que decide não foi pedida: a **47d** mede se
   a árvore põe o mesmo CC em mais de um grupo-folha, o que **duplicaria custo**. O QA
   reprovou a 1ª versão: `MAX` sobre as versões do cadastro deixava uma versão antiga
   mascarar a atual. Corrigido com `MIN` por versão e exclusão (`VALSIGN='E'`) tratada.
2. **O dono corrigiu o critério:** não há limiar de 95%. O relatório reflete todo
   lançamento, fiel ao registro (vazio aparece vazio). Tudo passou a medir em R$ e a fechar
   com o bloco 45; nova 47f para despesa **sem** centro de custo.
3. **A auditoria de placeholders** não achou placeholder vivo (o `400` foi medido: 280.823
   linhas). Achou pior: P02 e P06 se apoiavam em "0 linhas" **sem export salvo**, e o 29b
   exige 2 ou mais partidas de fornecedor no mesmo documento. Pelo bloco 28, havia **1**
   documento parcelado em 421. "O caixa está limpo" virou DESCONHECIDO até o 29c rodar.
4. **Nomes.** Editei `.sql` no lugar outra vez; o dono renomeou à mão, e a cópia dele (v7)
   saiu **sem o 29c**, porque foi feita no meio da minha edição. Conteúdo novo = v8; v6 e v7
   foram para `_obsoleto/` com o motivo no nome.

## Aprendizados (viraram memória)

- **Vazio sem export não é prova**, e vazio por construção também não. Antes de aceitar
  "vazio = ok": existe dado que esta consulta conseguiria devolver?
  (`vazio-sem-export-nao-e-prova`)
- **Arquivo que vai para terceiro nunca muda sob o mesmo nome**; e só se avisa que a versão
  existe depois de terminar todas as edições. (`sql-mudou-conteudo-muda-nome`)
- O `MAX` num agregado de verificação aponta para a direção que **esconde** o erro; o
  `MIN` ("sempre bateu"), para a que o mostra.

## Handoff

`C:\Users\fabriciosouza\budget-ti-thanner\RETOMADA-PROXIMA-SESSAO.md` — prompt para colar em
outra IDE, com o framework carregado em modo NON-ADMIN e o QA isolado em modelo diferente.
