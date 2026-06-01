<!-- required: Objetivo; Pré-condições; Passos de validação; Critérios de aceite; Evidências; Rollback / contingência; Sign-off -->
# Runbook de Validação (premium, ADR-050)

> **PISO de validação — default OBRIGATÓRIO em entrega premium.** Prova *que o entregável funciona*: passos
> reproduzíveis → resultado esperado → aceite binário → evidência. Diferente do manual (ensina a operar) e do
> deck (apoia decisão). Só dispensável por decisão consciente do dono em caso trivial.
> **Em domínio regulado** (o discovery declara as normas — saúde/alimentos/farmacêutico/financeiro/etc.,
> ADR-010/012 + `high-stakes-gate`): obrigatório e vira a espinha das evidências de qualificação/validação.
> Gerar: `tools/gen_exec_doc.py <este.md> --out-dir saida --formats md,docx,pdf`.
> Campo vazio → **NÃO PREENCHIDO** (nunca fabricar resultado/evidência).

## Objetivo
<o que este runbook valida (qual entregável/versão) e por quê — escopo da validação>

## Pré-condições
<ambiente, versão, dados de teste, dependências, acessos — o estado necessário ANTES de validar>

## Passos de validação
<lista numerada: passo → ação/comando → RESULTADO ESPERADO. Cada passo verificável de forma independente>

## Critérios de aceite
<o que prova PASS × FAIL (binário). Sem ambiguidade — "verde em todos os passos" ou condição equivalente>

## Evidências
<o que registrar como prova (saída, screenshot, hash, log) e onde guardar — rastreável à fonte>

## Rollback / contingência
<se a validação falhar: como reverter, a quem escalar, condição de parada>

## Sign-off
<quem valida, quem aprova, data — responsabilização (em regulado: assinatura/registro conforme a norma declarada)>
