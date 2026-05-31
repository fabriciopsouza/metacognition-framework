# ADR 029 — doc-intake: ingestão determinística de documentos (parse → chunk → manifesto, sem embeddings)

- Status: Aceito
- Data: 2026-05-31 · Decisores: dono + squad (architect)
- Onda: entrada determinística (v1.22.0) · Tipo: novo (1 capability `_shared/doc-intake` + 1 tool + teste-canário + 1 integração no discovery)
- Relaciona: `.agent/skills/discovery` (consome a capability), `_shared/anti-hallucination` (proveniência ancora afirmação), `_shared/traceability` (file-first), ADR-025 (sem transmissão), ADR-026 (`project_report.py` — mesmo padrão: tool Python tolerante + canário).

## Contexto

O discovery e o método sênior já exigem **fonte verificável** para afirmar. Mas quando a fonte é um
**documento** (PDF de norma, DOCX de requisito, XLSX de dados, PPTX, MD/TXT), o agente tende a "ler de
memória" ou a depender de extração ad-hoc não-reproduzível — violando file-first/anti-alucinação e
impossibilitando citar **proveniência** (qual trecho de qual arquivo). Faltava um mecanismo
**determinístico, offline e agnóstico** que transforme documentos em texto+chunks+manifesto auditável.

## Decisão (1 frase ativa)

Criar a capability `_shared/doc-intake` + `tools/doc_intake.py`: parse **determinístico** de
pdf/docx/xlsx/pptx/md/txt → **chunk** com overlap (fronteira de parágrafo) → **manifesto JSON** com
sha256 por arquivo e por chunk, **SEM embeddings** e **SEM rede**, degradando com segurança (formato
sem parser instalado vira `skipped`, não exceção) — invocado pelo discovery quando a entrada inclui documentos.

## Alternativas consideradas (≥3)

1. **Não fazer (status quo).** Agente lê documento de memória/ad-hoc; sem proveniência; não-reproduzível. **Rejeitada — é o gap.**
2. **RAG-vetorial / embeddings (vetor store + busca semântica).** Prós: recuperação por similaridade. Contras: **dependência externa pesada** (modelo de embedding + store), online, não-determinístico, "andaime morto" para a maioria dos casos; fere a régua §0 e o agnosticismo offline. **Rejeitada AGORA** — fica como ADR futuro com dependência **declarada** (decisão travada #4).
3. **Depender de ferramentas do harness para ler arquivos (Read/MCP).** Prós: já existem. Contras: não produz **manifesto auditável** nem chunking determinístico com sha de proveniência; varia por harness; não é citável de forma estável. **Rejeitada como base** (complementar, não substituto).
4. **Parse determinístico + chunk + manifesto, stdlib-first com parsers opcionais (ESCOLHIDA).** Prós: offline, determinístico, agnóstico, proveniência por sha; degrada se faltar lib; zero infra. Contras: sem OCR, sem layout rico (declarado nos limites). Passa o net-gain por **destravar capacidade inalcançável** (régua §0 cláusula c).

## Consequências

**Positivas:** discovery passa a citar documento por **proveniência verificável** (chunk id + sha256);
ingestão reproduzível e offline; `skipped/error/vazio` viram **gaps declarados** (não silêncio),
alinhando o método sênior. **Negativas:** sem OCR (PDF imagem-only → vazio, flagado); XLSX/PPTX
linearizam texto; parsers de binário são dependências opcionais (ausência = skip, não falha).
**Riscos:** formato de arquivo exótico/corrompido → `error` controlado (testado no canário). [DESCONHECIDO
não-bloqueante] cobertura de PDFs complexos varia com a versão do `pypdf`.

## Implementação (ponteiro após aceito)

- Ponteiro: branch `feat/v1.22.0-entrada-deterministica` · `2026-05-31` · grep `doc_intake` / `doc-intake`
- Artefatos: `tools/doc_intake.py` (CLI: target, `--out`, `--chunk-chars`, `--overlap`, `--with-text`);
  `tools/test_doc_intake.py` (canário: chunking sem perda + contíguo, manifesto determinístico,
  degradação graciosa em binário sem parser, validação de parâmetros — 4 testes verdes);
  `_shared/doc-intake/SKILL.md` (quando carregar / NÃO carregar / contrato / integração / limites);
  `.agent/skills/discovery/SKILL.md` §"Capability transversal: ingestão de documentos".
