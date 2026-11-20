# QA-evidence — adr-047-emenda1-bootstrap-preserva-settings

- **Data:** 2026-11-20
- **Veredito (passou):** True
- **Recomendacao:** aprovar_com_ressalvas

## Substitui vereditos anteriores deste bloco

- rodada 2 · 2026-11-20 · **aprovar_com_ressalvas** · sha `34562f02bee5` · agentId `a1b7e0a3e196f12ea`
  - cobria 10 caminho(s): bootstrap.py, tools/test_nonadmin.py, tools/test_squad_gate.py, behaviors/manifest.json …

## Problemas

| Sev | Local | Descricao |
|---|---|---|
| ALTA | bootstrap.py ps_available | Codex r1: pwsh funcionando com powershell.exe barrado dava falso SIM. So powershell.exe conta; teste A1 e sabotagem S7. |
| MEDIA | bootstrap.py activate_nonadmin | Codex r1: UnicodeEncodeError escapava. except (OSError, UnicodeError); teste A4; S8. |
| MEDIA | tools/test_nonadmin.py | Codex r1: sem teste de deteccao, --check, falha de troca, link. diagnostico_perfil extraida e testada; A1, A4, A5. |
| MEDIA | bootstrap.py main | Codex r1: 'hooks mantidos' com override ativo. Aviso 'continua ATIVO'; teste; S9. |
| MEDIA | tools/test_nonadmin.py | Sonnet r2: __pycache__ na raiz. sys.dont_write_bytecode no import. |
| MEDIA | bootstrap.py sondar_powershell | Sonnet r2: timeout virava falso NAO e gravava override. Sonda tri-estado; timeout repete com 60 s; indeterminado nao grava e sai 1; S11, S12. |
| BAIXA | bootstrap.py | Sonnet r2: mkstemp fora do try; mensagem 'politica restrita' enganosa. |
| BAIXA | behaviors/manifest.json, tools/test_squad_gate.py, guia/MODO-NON-ADMIN.md | Sonnet r2: justificativa envelhecida do settings.nonadmin.json; nota POSIX no guia. |
| BAIXA | bootstrap.py activate_nonadmin | Sonnet r2: regravacao reformata o settings.local.json; temporario orfao se o processo morrer. Limite declarado no guia e na spec 4c. |

## Verificacoes executadas (anti-fabricacao)

- prova de mecanismo com claude -p 2.1.326: hook roda sem local, nao roda com disableAllHooks true, volta a rodar ao remover (spec secao 2a)
- tools/test_nonadmin.py 23 de 23 (C1-C5, A1, A2, A4, A5, --check, trava em main com sonda sim/barrado/indeterminado e aviso de override ativo)
- 12 sabotagens em copia do bootstrap.py, todas reprovadas pelo caso certo (S1-S12)
- bateria completa run_canaries.py no estado final
