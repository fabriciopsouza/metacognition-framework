#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_knowledge_catalog.py — testes para knowledge_catalog.py (ADR-068).

Cobre: parse de relatório, BM25 scoring, build/recall/patterns, CLI exits.
Todos os testes usam apenas stdlib + fixtures inline (sem I/O real de prod).
"""
import json
import math
import os
import sys
import tempfile
import textwrap
import unittest

# Adiciona tools/ ao path para import direto
sys.path.insert(0, os.path.dirname(__file__))
import knowledge_catalog as kc


# ── Fixtures ──────────────────────────────────────────────────────────────────

REPORT_FULL = textwrap.dedent("""\
    # Execution-report — sessão fictícia (ADR-068 test fixture)

    > Sessão 2026-06-01 · descoberta de 2 gaps críticos

    - **Tokens:** NÃO MEDIDO
    - **Tempo:** NÃO MEDIDO
    - **Turnos:** NÃO MEDIDO
    - **Arquivos tocados:** tools/foo.py, docs/bar.md
    - **Testes:** canários verdes (3/3)
    - **Rodadas de retrabalho:** 1

    ## Placar gate × achado (quem pegou o quê)

    | Achado | Quem pegou | Gate que deveria ter pego |
    | Bug de encoding em stdout | qa-critic (MÉDIO) | guard de stdout — adicionado |
    | Regex sem ancoragem | agente | revisão de código |

    ## Detecção: framework × humano (mecanismo vs. revisão humana)

    - Mecanismo pegou: effect-gate barrou `rm -rf` destrutivo
    - Humano (dono) trouxe evidência do Kaspersky via CSV

    ## Gaps (não-bloqueantes detectados — flagados, não silenciados)

    - Anonimização por regex não-exaustiva: token fora do map passa
    - Fallback .ps1 não carimba liveness

    ## Melhorias (do framework/processo)

    - Auditor de liveness universal — falha de hook nunca silenciosa
    - Honestidade da vitrine mecanizada (gates h/i de drift)

    ## Boas práticas (o que funcionou — reutilizável)

    - file-first salvou 2x: descobriu que feature já existia
    - Testar contra arquivos reais revela falsos-positivos do léxico

    ## Lições por skill (agnóstico de domínio)

    - **dev:** gate determinístico (regex/arquivo) > LLM-no-CI
    - **discovery:** checar se feature já existe antes de construir (régua §0)
    - **qa-critic:** hipótese-default-bug pega drift que o autor normaliza
""")

REPORT_EMPTY = textwrap.dedent("""\
    # Relatório vazio — sem seções de aprendizado

    - **Tokens:** NÃO MEDIDO
""")

REPORT_CONTINUACAO = textwrap.dedent("""\
    # Execution-report — sessão com continuação

    > Sessão 2026-06-02

    ## Gaps (não-bloqueantes)

    - Gap de continuação: sem tracking de features antigas

    ## Lições por skill

    - **pmo:** manter WIP-limit previne overload
    - **architect:** EMENDA > ADR novo quando gene já existe

    ## Continuação 2026-06-02 — ADRs extras

    > Sessão estendida

    ### Lições novas (alto valor — agnósticas)

    - Adoção cai pela metade por cada passo manual recorrente
""")


# ── Testes de parse ───────────────────────────────────────────────────────────

class TestParseReport(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _write(self, name: str, content: str) -> str:
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return path

    def test_full_report_extracts_all_sections(self):
        path = self._write("execution-report.md", REPORT_FULL)
        entry = kc.parse_report(path)
        self.assertIsNotNone(entry)
        self.assertGreater(len(entry["gaps"]), 0)
        self.assertGreater(len(entry["melhorias"]), 0)
        self.assertGreater(len(entry["boas_praticas"]), 0)
        self.assertIn("dev", entry["licoes"])
        self.assertIn("qa-critic", entry["licoes"])
        self.assertGreater(len(entry["detecao"]), 0)

    def test_full_report_date_extracted(self):
        path = self._write("execution-report.md", REPORT_FULL)
        entry = kc.parse_report(path)
        self.assertEqual(entry["date"], "2026-06-01")

    def test_empty_report_returns_none(self):
        path = self._write("empty.md", REPORT_EMPTY)
        entry = kc.parse_report(path)
        self.assertIsNone(entry)

    def test_continuacao_lições_merged(self):
        path = self._write("cont.md", REPORT_CONTINUACAO)
        entry = kc.parse_report(path)
        self.assertIsNotNone(entry)
        # lições devem conter pmo e architect (seção principal)
        self.assertIn("pmo", entry["licoes"])
        self.assertIn("architect", entry["licoes"])

    def test_report_id_is_deterministic(self):
        path = self._write("execution-report.md", REPORT_FULL)
        e1 = kc.parse_report(path)
        e2 = kc.parse_report(path)
        self.assertEqual(e1["report_id"], e2["report_id"])

    def test_tokens_full_built(self):
        path = self._write("execution-report.md", REPORT_FULL)
        entry = kc.parse_report(path)
        self.assertIn("_tokens_full", entry)
        self.assertGreater(len(entry["_tokens_full"]), 0)

    def test_placar_table_extracted(self):
        path = self._write("execution-report.md", REPORT_FULL)
        entry = kc.parse_report(path)
        self.assertGreater(len(entry["placar"]), 0)

    def test_nonexistent_file_returns_none(self):
        entry = kc.parse_report("/nao/existe/relatorio.md")
        self.assertIsNone(entry)


# ── Testes de BM25 ────────────────────────────────────────────────────────────

class TestBM25(unittest.TestCase):

    def _make_entries(self, texts):
        entries = []
        for i, text in enumerate(texts):
            entries.append({
                "report_id": f"id{i}",
                "date": "2026-01-01",
                "source": f"fake_{i}.md",
                "skills": [],
                "route": "squad",
                "gaps": [],
                "melhorias": [],
                "boas_praticas": [],
                "licoes": {},
                "detecao": [],
                "_tokens_full": text,
            })
        return entries

    def test_recall_returns_most_relevant(self):
        entries = self._make_entries([
            "gate determinístico falha de hook auditor de liveness",
            "discovery elicitação briefing requirements agnóstico",
            "gate liveness hook silencioso audit trail mecanismo",
        ])
        result = kc.recall(entries, "gate liveness hook", top_n=1)
        self.assertEqual(len(result), 1)
        # Deve retornar um dos que contém "gate liveness hook"
        self.assertIn(result[0]["report_id"], ["id0", "id2"])

    def test_recall_empty_entries_returns_empty(self):
        result = kc.recall([], "qualquer query")
        self.assertEqual(result, [])

    def test_recall_empty_query_returns_first_n(self):
        entries = self._make_entries(["a b c", "d e f", "g h i"])
        result = kc.recall(entries, "", top_n=2)
        self.assertEqual(len(result), 2)

    def test_bm25_score_increases_with_tf(self):
        idx = kc._build_bm25_index(self._make_entries([
            "gate gate gate fail",
            "gate fail",
        ]))
        s1 = kc._bm25_score(["gate"], idx["tokenized"][0], idx)
        s2 = kc._bm25_score(["gate"], idx["tokenized"][1], idx)
        self.assertGreater(s1, s2)

    def test_bm25_unknown_term_scores_zero(self):
        idx = kc._build_bm25_index(self._make_entries(["hello world"]))
        score = kc._bm25_score(["xyzzy_nao_existe"], idx["tokenized"][0], idx)
        self.assertEqual(score, 0.0)

    def test_bm25_empty_index_scores_zero(self):
        idx = {"N": 0, "avgdl": 1.0, "df": {}, "tokenized": []}
        score = kc._bm25_score(["gate"], [], idx)
        self.assertEqual(score, 0.0)


# ── Testes de build/recall/patterns (integração com tmp dir) ──────────────────

class TestBuildRecallPatterns(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.intake = os.path.join(self.tmp, "intake")
        self.out    = os.path.join(self.tmp, "catalog")
        os.makedirs(self.intake)

    def _write_report(self, name, content):
        path = os.path.join(self.intake, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return path

    def test_build_creates_all_files(self):
        self._write_report("r1.md", REPORT_FULL)
        rc = kc.cmd_build(self.intake, self.out)
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "catalog.json")))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "session-insights.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "patterns.md")))

    def test_build_empty_intake_returns_2(self):
        rc = kc.cmd_build(self.intake, self.out)
        self.assertEqual(rc, 2)

    def test_build_catalog_json_valid(self):
        self._write_report("r1.md", REPORT_FULL)
        kc.cmd_build(self.intake, self.out)
        with open(os.path.join(self.out, "catalog.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        # _tokens_full NÃO deve estar no JSON salvo (só reconstruído no load)
        self.assertNotIn("_tokens_full", data[0])

    def test_catalog_json_no_tokens_full(self):
        """_tokens_full é campo interno; nunca persiste em catalog.json."""
        self._write_report("r1.md", REPORT_FULL)
        kc.cmd_build(self.intake, self.out)
        with open(os.path.join(self.out, "catalog.json"), encoding="utf-8") as fh:
            raw = fh.read()
        self.assertNotIn("_tokens_full", raw)

    def test_recall_no_catalog_returns_2(self):
        rc = kc.cmd_recall("gate liveness", self.out, top_n=3)
        self.assertEqual(rc, 2)

    def test_recall_after_build_returns_markdown(self, capsys=None):
        self._write_report("r1.md", REPORT_FULL)
        kc.cmd_build(self.intake, self.out)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = kc.cmd_recall("gate liveness hook", self.out, top_n=2)
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("##", out)

    def test_patterns_after_build_creates_file(self):
        self._write_report("r1.md", REPORT_FULL)
        kc.cmd_build(self.intake, self.out)
        rc = kc.cmd_patterns(self.out)
        self.assertEqual(rc, 0)
        with open(os.path.join(self.out, "patterns.md"), encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("Padrões", content)

    def test_multiple_reports_merged_in_patterns(self):
        self._write_report("r1.md", REPORT_FULL)
        self._write_report("r2.md", REPORT_CONTINUACAO)
        kc.cmd_build(self.intake, self.out)
        rc = kc.cmd_patterns(self.out)
        self.assertEqual(rc, 0)

    def test_session_insights_md_non_empty(self):
        self._write_report("r1.md", REPORT_FULL)
        kc.cmd_build(self.intake, self.out)
        with open(os.path.join(self.out, "session-insights.md"), encoding="utf-8") as fh:
            content = fh.read()
        self.assertGreater(len(content.strip()), 0)
        self.assertIn("ADR-068", content)


# ── Testes de tokenização ─────────────────────────────────────────────────────

class TestTokenize(unittest.TestCase):

    def test_normalizes_accents(self):
        tokens = kc._tokenize("Lição de ação mecanização")
        self.assertIn("licao", tokens)
        self.assertIn("acao", tokens)

    def test_lowercases(self):
        tokens = kc._tokenize("Gate GATE Gate")
        self.assertEqual(tokens, ["gate", "gate", "gate"])

    def test_empty_string(self):
        self.assertEqual(kc._tokenize(""), [])

    def test_strips_punctuation(self):
        tokens = kc._tokenize("gate-liveness: hook (ADR-061)")
        self.assertIn("gate", tokens)
        self.assertIn("liveness", tokens)
        self.assertIn("hook", tokens)
        self.assertIn("adr", tokens)


# ── Testes de snippet ─────────────────────────────────────────────────────────

class TestSnippet(unittest.TestCase):

    def test_short_text_unchanged(self):
        self.assertEqual(kc._snippet("hello"), "hello")

    def test_long_text_truncated(self):
        text = "x" * 200
        s = kc._snippet(text)
        self.assertLessEqual(len(s), kc.MAX_SNIPPET)
        self.assertTrue(s.endswith("…"))

    def test_exact_max_not_truncated(self):
        text = "x" * kc.MAX_SNIPPET
        self.assertFalse(kc._snippet(text).endswith("…"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
