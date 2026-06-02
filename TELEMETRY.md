# Telemetria de processo — transparência, privacidade e opt-out (ADR-052)

> **TL;DR:** ao usar este framework numa distribuição (clone público/non-admin/premium), o fechamento
> de um bloco de trabalho pode gerar um **relatório de PROCESSO anonimizado e estruturado** em
> `telemetry/`. Ele contém **apenas sinais de processo codificados** — onde um gate disparou, onde um
> hook/regra falhou, onde você corrigiu, quantas rodadas de retrabalho — **nunca o conteúdo do seu
> trabalho, nunca texto livre, nunca dado pessoal**. **Nada é enviado automaticamente.** Se você quiser
> ajudar a melhorar o framework, **abre um PR** com esse arquivo para o repositório canônico — e esse PR
> é o seu consentimento. Não quer nem gerar? **Desligue** (ver abaixo). Ao baixar o framework, você toma
> ciência desta política.

## Por que existe

O placar "qual gate pegou o quê / onde o processo falhou" foi o insumo que mais acelerou a melhoria do
framework. Instalações de terceiros batem nos **mesmos pontos de falha de processo** (um gate que não
disparou, uma prosa que não pegou, uma correção manual). Capturar **esse sinal de processo** — e só ele —
permite consertar o método para todos. **Não** queremos (nem coletamos) o que você está construindo.

## Dois tiers (detecção automática, sem config)

| | **Tier OWNER** (repo-fonte do mantenedor) | **Tier EXTERNAL** (qualquer distribuição) |
|---|---|---|
| Detecção | `docs/_private/` existe | `docs/_private/` ausente (export-clean o remove) |
| Conteúdo | Relatório completo, sem filtro | **Só sinais de processo codificados** |
| Texto livre / domínio | Permitido (é o repo privado do dono) | **Proibido** (rejeitado por whitelist) |
| Onde grava | `docs/_private/_intake/` (não distribuído) | `telemetry/` (versionável pelo usuário) |
| Opt-out | n/a (repo do próprio dono) | **Sim** (ver abaixo) |
| Transmissão | nenhuma | nenhuma automática — só por **PR que você abre** |

## O que o tier EXTERNAL registra (e o que NUNCA registra)

**Registra (codificado):**
- `gates_fired` — quais gates dispararam e o resultado (`pass`/`fail`/`override`/`skip`).
- `failure_points` — **onde o processo falhou**: mecanismo (`hook`/`gate`/`tool`/`prose`) + id + tipo de
  falha (`missed`/`misfired`/`absent`/`bypassed`/`false-positive`) + junção (J0–J5).
- `correction_events` — **onde você corrigiu** (codificado): `rewind`/`override`/`redirect`/`reject`/`clarify` + junção + nº do turno.
- Metadados de processo: `route`, `execution_mode`, `turnos`, `retrabalho_rodadas`, `framework_version`, um `session_id` opaco.
- `tokens` — apenas se houver telemetria do host; senão literalmente `NÃO MEDIDO` (nunca inventado).

**NUNCA registra:** o texto dos seus prompts, conteúdo de arquivos, nomes de cliente/projeto, segredos,
caminhos, ou qualquer texto livre. Isso é **garantido por mecanismo**, não por confiança (ver abaixo).

## Como "zero vazamento" é garantido (mecanismo, não promessa)

O validador (`tools/execution_report.py`, modo external) é uma **whitelist de schema**: cada linha do
relatório tem de casar `<chave>: <valor>` onde a chave é de um vocabulário fixo e o valor é um **enum
controlado, inteiro, versão ou hash opaco**. Qualquer linha de texto livre, ou um valor fora do enum, é
**rejeitada (FAIL)**. PII (e-mail/CPF/CNPJ/telefone/strings longas) é barrada por heurística adicional.
Não há campo onde caiba conteúdo de domínio. Lição do incidente de 2026-05-31: anonimização tem de ser
**gate verificável**, não confiança no agente.

## LGPD / base legal

Como o payload é estruturado e **não-pessoal**, ele está **fora do escopo da LGPD** (Art. 12 — dado
anonimizado não é dado pessoal). Por isso:
- **Geração:** coberta por **opt-out documentado** (este arquivo + `SECURITY.md` + `LICENSE`) — sem popup.
- **Transmissão:** só acontece se **você abrir um PR** com o arquivo. Esse ato é **consentimento
  explícito, informado e específico** (LGPD Art. 8) — você revê o arquivo (é legível) antes de enviar.

## Como desligar (opt-out) — a geração

Qualquer um destes desliga a geração do tier external:
- criar `.claude/no-telemetry.lock` (este projeto) ou `~/.claude/no-telemetry.lock` (global);
- definir a variável de ambiente `FRAMEWORK_NO_TELEMETRY=1`.

## Como contribuir de volta (opcional)

1. Após um bloco, confira `telemetry/telemetry-report.md` (é legível).
2. Se quiser ajudar: faça commit dele no seu fork e abra um **PR** para
   `github.com/fabriciopsouza/metacognition-framework`. O PR é o consentimento.
3. O mantenedor agrega esses sinais para consertar gates/regras que falharam — para todos.
