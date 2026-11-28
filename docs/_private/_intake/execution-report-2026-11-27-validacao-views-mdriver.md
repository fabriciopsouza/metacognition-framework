# Relatório de execução — validação de 5 views contra o sistema de origem (03 a 06/11/2026)

**Forma:** OWNER (privado, ADR-062). Domínio: Vibra, MDriver. Conhecimento de domínio registrado na biblioteca Vibra,
`empresas/vibra/dados-gcp/mdriver-telas-e-views-rf.md` (VW-01 a VW-10).

## Erros do agente e o que os pegou

| # | Erro | Quem pegou | Lição |
|---|---|---|---|
| 1 | Período do plano vago ("2 dias", "mês recente") | Dono | Período de captura é parâmetro: data exata, com ano |
| 2 | Motor dizia "sem divergência" com 2% do universo comparado | Revisão Fable | Cobertura é saída obrigatória (DB-27-11-D) |
| 3 | Aplicou correção prescrita pela revisão sem testar (filtro por data de início) | Dado real das capturas | Prescrição do revisor é hipótese (DB-27-11-C) |
| 4 | Afirmou "cerca de 400 linhas" como limite da tela | Revisão Sonnet | O corte era por volume: medir antes de afirmar |
| 5 | Tratou a Chegada como divergência real | Captura no layout novo | Layout da tela muda: recapturar antes de levar à TI |
| 6 | Leu o arquivo errado como a captura nova | Trava de período do motor | A trava mecânica pegou o que a atenção não pegou |
| 7 | Exigiu IRIS como fonte; o dono preferiu telas | Dono | Perguntar antes a fonte que o dono consegue operar |
| 8 | Levou "grupo de bombas vazio" como achado à TI | Comparação com a tela (0 de 64 também vazio) | Conferir a tela de origem antes de listar um campo vazio |

Os erros 6 e 7 são relato da sessão; os demais têm fonte nos arquivos da pasta `views-rf-mdriver`.

## Acertos que vale repetir
- Trava de base e período do export, print do filtro obrigatório, consolidação por regra: mecanismos, não prosa.
- Escada de modelos: Sonnet nos números, Fable no mérito. O Fable reprovou duas vezes com achados novos e reais.
- Busca do menu da ferramenta de origem achou relatórios sem caminho registrado.
- Verificação cruzada por segunda tela (soma de medições contra o relatório de Bateladas) resolveu um campo sem fonte direta.

## Limites do ambiente
- Hub multi-IA não configurado e sem CLI de Gemini ou Codex: revisão multi-IA indisponível; usada a escada de modelos.
- Push de outro repositório a partir da sessão do framework: bloqueado em outubro; liberado em novembro: PRs #57 do mdriver-bq-analytics e #227 do framework mesclados em 26/11/2026 por esta sessão.
- Suíte de canários passa de 10 minutos (DB-27-11-B).
