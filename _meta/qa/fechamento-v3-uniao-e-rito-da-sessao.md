# QA-evidence — fechamento-v3-uniao-e-rito-da-sessao

- **Data:** 2026-09-23T00:00:00Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| BAIXA | tools/test_squad_gate.py::_ev_artefato | O fail-closed sob quebra da excecao do auto-artefato e' INCIDENTAL, nao declarado: ele depende de o arquivo sintetico `_meta/qa/<slug>.json` nao existir de fato. Se um dia existir um artefato com esse nome, a protecao muda de comportamento sem ninguem notar. CORRECAO: docstring de `_ev_artefato` passou a declarar a dependencia, com o mecanismo (ramo `_blob_indexado`, `git rev-parse :<path>` codigo 128, `_git()` None) e a medicao do critico. |
| BAIXA | execution-report, tabela 'De onde saimos' | A contagem '37 para 36 trabalhos' nao e' re-verificavel: o armazem `~/.claude/trabalhos/` e' externo ao repo e compartilhado, e a contagem viva subiu para 38 por registros criados no mesmo dia. CORRECAO: Nao e' alegacao falsa — e' numero que envelhece por natureza do armazem. Dois dos registros novos sao exatamente os achados que a FASE 6 do proprio report descreve. |
| MEDIA | processo de commit | Dois artefatos de proveniencia diferente entrando juntos numa arvore que teve 5 sessoes vivas. CORRECAO: `git add` NOMEADO por caminho, nunca `-A`; e este veredito registrado DEPOIS do add, porque o carimbo `blobs_revisados` le o INDICE — registrar antes faria o gate barrar com 'FALTA qa_critic' sem dizer a causa. |

## Verificacoes executadas (anti-fabricacao)

- critico forcou `sg._artefato_do_proprio_veredito` para False por monkeypatch e executou os 5 testes de uniao: `test_uniao_dois_vereditos_parciais_cobrem_o_conjunto` e `test_uniao_NAO_cobre_caminho_que_ninguem_revisou` foram a FAIL; os outros 3 nao dependem da excecao e seguiram OK
- critico identificou o mecanismo do fail-closed: sem a excecao, `_recente_o_bastante` cai no ramo `_blob_indexado`, e `git rev-parse :_meta/qa/veredito-uniao-a.json` sai com codigo 128 porque o caminho sintetico nao existe em disco nem no indice, entao `_git()` devolve None
- critico aplicou a mutacao real `uniao vira any` e mediu que 4 dos 5 testes a matam
- critico comparou `git show HEAD:tools/test_squad_gate.py` com o staged: 96 testes em cada, nomes identicos, nenhum removido nem enfraquecido; um ganhou asserção de sanidade a mais
- critico procurou saida silenciosa (return/skip/continue/assert True) nos trechos alterados e nao achou — era o defeito exato que derrubou a v2
- autor rodou `python tools/test_squad_gate.py`: 96 PASS / 0 FAIL
- autor rodou `python tools/test_mutacao_squad_gate.py` com a v3 em disco: PASS (37/37 mutacoes mortas)
- autor mediu, e o numero NAO distingue as versoes: a v1 commitada tambem da 37/37 nesta maquina — foi assim que o defeito passou despercebido
- critico recontou programaticamente os [v]/[ ] das 7 FASES do execution-report e recalculou round(pct*12/100): as 7 batem, nenhum percentual nem barra divergente
- critico conferiu as afirmacoes do report contra as fontes reais: git show 5305ae2 --stat (137 arq/22.649 ins), gh pr view 142 (MERGED efa7374), gh api branches/main/protection (required: canarios-local), e o log literal do job ubuntu — que bate caractere a caractere com o que o report cita
