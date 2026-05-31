# RESILIÊNCIA DE ACESSO

> A proteção real do seu trabalho **não é a chave SSH/credencial no PC** — é o
> **recovery da sua CONTA GitHub** + o hábito de **pushar cedo**. Este guia trata o
> risco que o backup de código não cobre: perder o **acesso** ao código que já subiu.

## Modelo de ameaça (o que pode dar errado)
1. **PC morre / é roubado / disco corrompe** no meio de um bloco. → Tudo que **não foi pushado** se perde.
2. **Sessão cai de madrugada** (tokens, crash, queda de energia) durante execução autônoma. → Idem.
3. **Você perde a chave local** (reinstalou o SO, trocou de PC). → O código no GitHub está intacto, mas **você não consegue acessá-lo** se também perdeu o acesso à conta.

> Os itens 1–2 são resolvidos por **pushar cedo**. O item 3 — o mais subestimado — é
> resolvido por **recovery de conta**, não por backup da chave.

## Por que recovery de CONTA > chave local
A chave SSH / PAT no seu PC é **descartável**: some junto com o PC. O que **não** pode
sumir é a capacidade de **provar que a conta é sua** e gerar uma chave nova. Logo, a
prioridade de resiliência é, nesta ordem:

1. **2FA com método de recuperação guardado FORA do PC** — códigos de backup (recovery
   codes) impressos/num cofre de senhas em outro dispositivo; app autenticador com backup
   na nuvem; chave de segurança física (FIDO2) guardada separada.
2. **E-mail de recuperação acessível de outro lugar** (não só no PC que pode sumir).
3. **Senha num gerenciador sincronizado** (não só no chaveiro local do PC).
4. Só **depois** disso: a chave SSH/PAT local — que você **regenera** assim que recupera a conta.

> Teste binário: *se este PC sumisse agora, em quanto tempo você recupera acesso de
> escrita ao repo de outro dispositivo?* Se a resposta depende de algo que só existe
> neste PC, o recovery está frágil.

## Pushar cedo — a disciplina que protege 1 e 2
- **Commit + push por artefato concluído**, não "no fim do bloco". Cada push move o
  trabalho para o lugar que sobrevive ao PC.
- Em **execução autônoma longa** (noturna), pushar a cada item é o ponto de restauração:
  se a sessão cair, o trabalho pushado está salvo e a retomada começa do primeiro item pendente.
- **Branch de trabalho pushada** (`git push -u origin <branch>`) desde o primeiro commit —
  não acumule commits locais "para empurrar depois".

## O gate que torna isso mecânico (ADR-030)
`tools/hooks/consistency-gate.ps1` tem a dimensão **unpushed**: conta os commits à frente
do upstream e **avisa** quando há trabalho local não-protegido (ou branch sem upstream).
Rode no `/checkpoint` e antes de fechar o dia:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/hooks/consistency-gate.ps1
```
`não-pushados: 0` = tudo que existe está no GitHub. Qualquer número > 0 = risco aberto.

## Recovery — o roteiro (PC novo / acesso perdido)
1. **Recupere a CONTA GitHub** (2FA recovery codes → e-mail de recuperação → suporte, nessa ordem).
2. **Gere credencial nova** no PC novo: `gh auth login` (ou nova chave SSH + adicionar em Settings → SSH keys).
3. **Clone** o repo: `git clone <url>` — todo o trabalho pushado volta.
4. **Retome** pelo padrão de salvaguarda: abra a branch de trabalho, leia o arquivo de
   retomada (se houver, em `docs/_intake/`) e continue do primeiro item pendente.

> Resumo: **backup de código** o GitHub já faz. O que **você** precisa garantir é
> **backup de ACESSO** (recovery de conta) + **push cedo** (para não haver nada só no PC).
