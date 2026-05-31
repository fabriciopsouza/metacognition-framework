---
name: doc-intake
description: "Ingestão determinística de documentos (pdf/docx/xlsx/pptx/md/txt) → chunk → manifesto auditável, OFFLINE e SEM embeddings. Carregar quando o pedido traz ARQUIVOS/DOCUMENTOS como fonte (anexos, pasta de specs, relatórios, planilhas, normas em PDF) e o agente precisa extrair texto de forma reproduzível antes de elicitar/decidir — tipicamente chamada pelo discovery. NÃO carregar para conversa sem documentos, nem para RAG-vetorial/busca semântica (isso é ADR futuro com dependência externa declarada). NÃO é OCR (PDF imagem-only degrada para 'vazio')."
version: 1.0.0
source: "ADR-029 (v1.22.0) — entrada determinística; decisão travada #4 (parse sem embeddings, offline/agnóstico)"
last_review: 2026-05-31
---

# doc-intake — Ingestão determinística de documentos (fonte única)

Capability agnóstica de domínio: transforma documentos brutos em **texto + chunks +
manifesto JSON** reproduzível, para o discovery (ou qualquer papel) raciocinar sobre
o conteúdo **sem** depender da memória do modelo nem de serviço externo.

## Quando carregar
- O pedido inclui **arquivos** como fonte: PDF de norma, DOCX de requisito, XLSX de
  dados, PPTX de apresentação, MD/TXT de spec.
- Antes de elicitar/decidir sobre o conteúdo de um documento — para citar trechos com
  **proveniência** (arquivo + offset + sha256), não de memória.

## Quando NÃO carregar
- Conversa sem documento anexo; pedido puramente conceitual.
- **Busca semântica / RAG-vetorial / embeddings** — fora de escopo por decisão (#4);
  é ADR futuro com dependência externa (vetor store) **declarada**. Aqui é só parse+chunk.
- **OCR** (PDF só-imagem, scans): não suportado; degrada para "vazio" (flag no manifesto).

## Contrato (o tool)
`tools/doc_intake.py <arquivo-ou-pasta> [--out manifest.json] [--chunk-chars 1200] [--overlap 150] [--with-text]`

- **Determinístico:** mesmo input → mesmo manifesto (sem timestamp; sha256 por arquivo
  e por chunk; ordem estável; chunking em fronteira de parágrafo).
- **Degrada com segurança:** formato cujo parser opcional não está instalado vira
  `status: "skipped: requer '<lib>'"` — os demais arquivos seguem. NUNCA derruba o run.
- **Offline:** zero rede, zero transmissão (alinha ADR-025).
- **Parsers opcionais:** pdf→`pypdf`, docx→`python-docx`, xlsx→`openpyxl`, pptx→`python-pptx`.
  Ausentes → skip declarado. `.md/.txt` usam só stdlib (sempre funcionam).

### Manifesto (forma)
```
{ "manifest_version":1, "embeddings":false,
  "summary": {"n_files","n_ok","n_skipped","n_error","n_chunks"},
  "files": [ {"path","format","bytes","sha256","extractor","status","n_chars",
              "n_chunks","chunks":[{"id","ordinal","char_start","char_end","sha256"[,"text"]}]} ] }
```

## Como o discovery usa (integração)
1. Detectou documento(s) como fonte → rodar `doc_intake.py <pasta> --out intake-manifest.json`.
2. Ler o manifesto; para cada afirmação derivada de um documento, **citar a proveniência**
   (`id` do chunk + `sha256`) — sustenta o file-first e o anti-alucinação (afirmação
   ancorada em fonte verificável, não em memória).
3. `status: skipped/error/vazio` é **gap declarado**, não silêncio: vai para os
   "Gaps não-bloqueantes" do `research-brief.md`/`requirements.md` (método sênior).

## Limites (declarados, não escondidos)
- Texto-extraível apenas (sem OCR, sem layout/tabela-estruturada rica em PDF).
- XLSX/PPTX extraem texto linearizado (não preservam fórmula/posicionamento).
- Chunking é por chars com overlap — bom para contexto; não é parser sintático de domínio.
