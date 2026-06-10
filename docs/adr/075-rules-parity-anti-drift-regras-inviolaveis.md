# ADR 075 — rules-parity: anti-drift das 4 regras invioláveis (erro #4 do Gemini, sem violar a SSoT)

- Status: **Aceito** (2026-06-10 — gate: CI verde na suíte + qa-critic adversarial; dogfood: o canário achou e reconciliou um drift real no boot) · Data: 2026-06-10 · Decisores: dono + squad
- Onda: anti-bypass cross-IA (item E3 do `docs/PLANO-ANTI-BYPASS-CROSS-IA.md`) · Tipo: **adição** justificada pela régua §0(c) — destrava garantia inalcançável por prosa (o próprio drift achado prova que prosa não bastava).
- Relaciona: AGENT-FRAMEWORK §6.5 (Single source of truth — `_shared/` é a fonte; ninguém recopia regra), ADR-020 (linter de agnosticismo do núcleo), ADR-027/028 (precedência/roteamento). Origem cross-IA: erro sistêmico **#4 do Gemini** ("dual prompt authority / silent drift": `GEMINI_Metcognition.txt` × `GEMINI-FRAMEWORK.md` como fontes simultâneas).

## Contexto

A auditoria dos relatórios cross-IA do Gemini (2026-06-10) listou "dual prompt authority / silent drift" como erro sistêmico: dois arquivos de prompt coexistiam como fontes-de-verdade sem mecanismo que detectasse divergência. **File-first no repo vivo** mostrou que este framework **estruturalmente previne** a versão exata do Gemini (princípio §6.5: SSoT em `_shared/`, todo o resto **referencia**, ninguém recopia). **Porém** os arquivos de autoridade mantêm **digestos por referência** das 4 regras invioláveis (CLAUDE.md lista; AGENT-FRAMEWORK.md cita "4 regras invioláveis (…)"; AGENTS.md delega a `.agent/rules/`) — e esses digestos **podiam divergir em silêncio**: o canário, ao nascer, achou um drift real — AGENT-FRAMEWORK.md nomeava a 4ª regra como "releitura forçada" enquanto CLAUDE.md (e o CLAUDE.md global, autoritativo) e §6.1 dizem **"NÃO SEI / nunca inventar"** (anti-alucinação).

## Decisão (1 frase ativa)

Criar `tools/check_rules_parity.py` (+ canário `test_rules_parity.py`) **fail-closed na suíte CI** que detecta **drift entre os digestos** das 4 regras invioláveis — **NÃO** paridade byte-a-byte de blocos duplicados (isso violaria §6.5 e exigiria a duplicação que o princípio proíbe): (1) CLAUDE.md tem o bloco com **exatamente 4** itens cobrindo os 4 conceitos canônicos; (2) AGENT-FRAMEWORK.md usa a **mesma contagem (4)** e nomeia os 4 conceitos; (3) AGENTS.md **referencia a SSoT** (`_shared/`/`.agent/rules/`) em vez de redefinir — guarda direta anti dual-authority. Assinaturas por **conceito** (tolerante a redação, intolerante a sumiço). O drift achado foi reconciliado (AGENT-FRAMEWORK.md:124 → "NÃO SEI/nunca-inventar").

## Alternativas consideradas

1. **Paridade byte-a-byte de blocos de regras replicados nos 3 arquivos.** Exigiria **duplicar** o corpo das regras nos arquivos — **viola §6.5** ("ninguém recopia regra") e geraria manutenção redundante. **Rejeitada (contradiz a constituição do framework).**
2. **Não fazer (status quo).** O drift "releitura forçada × NÃO SEI" provou que digestos divergem em silêncio sem ninguém ver. **Rejeitada — é o gap (erro #4 do Gemini no nosso idioma).**
3. **Detector de drift por conceito + checagem de delegação à SSoT (ESCOLHIDA).** Honra §6.5 (não duplica; reforça a referência), mecaniza anti-drift fail-closed, achou bug real no nascimento. Limite: assinaturas por conceito são uma heurística — wording muito criativo poderia escapar (mitigado: as 4 regras têm nome estável/aprovado).

## Consequências

**Positivas:** o drift entre arquivos de autoridade deixa de ser ponto cego; reforça §6.5 (delegação à SSoT em AGENTS.md vira invariante checado); o erro #4 do Gemini fica coberto **sem** importar a duplicação que o causou. **Validação por dogfood:** o canário achou e reconciliou 1 drift real (4ª regra) ao nascer [CONFIRMADO]. **Negativas/limite (declarado, honesto):** assinaturas por conceito são heurística (não prova semântica) — uma reescrita que troque o **sentido** mantendo as palavras-chave passaria; é a fronteira do mecanizável (o resto é julgamento, P11). Os ponteiros (CLAUDE/AGENTS/AGENT-FRAMEWORK) são convenção deste repo — o método é agnóstico, a config não. O CLAUDE.md **global** (`~/.claude`) não é versionado aqui → fora do alcance do canário (declarado).

## Implementação (ponteiro)

- Artefatos: `tools/check_rules_parity.py` (linter; `audit(root)` testável) + `tools/test_rules_parity.py` (canário: repo real PASS + 3 classes de drift pegas em fixture). Registrado em `capabilities.json` (`rules-parity-guard`, enforcement fail-closed). Reconciliação dogfood: `AGENT-FRAMEWORK.md` §1 (4ª regra). Suíte: `run_canaries.py`.
