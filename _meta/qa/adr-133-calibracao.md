# QA-evidence — adr-133-calibracao

- **Data:** 2026-10-31T01:43:04Z
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| MEDIA | tools/test_ux_gate.py | r1: borda de cabecalho com 2 palavras sem teste de passa |
| MEDIA | tools/test_ux_gate.py | r1: override de titulo e controle por perfil escapava |
| MEDIA | tools/ux_gate.py PERFIS | r2: override que baixa o limite por perfil escapava (mesma familia da r1) |
| BAIXA | SKILL.md e calibracao-dono.md | r1 a r3: tamanhos do cartao e descricoes de perfil sem fonte; desdobramentos do norte sem INFERIDO |
| BAIXA | tools/test_ux_gate.py | r3: perfil novo em PERFIS nao deixava o teste vermelho |

## Verificacoes executadas (anti-fabricacao)

- python tools/test_ux_gate.py
- python tools/test_adr_changelog_sync.py
- python tools/test_marketing_claims.py
- sabotagem em copia: cada limite (2/2/4/8) para cima e para baixo, limite por perfil, perfil removido e perfil novo: todos vermelhos
