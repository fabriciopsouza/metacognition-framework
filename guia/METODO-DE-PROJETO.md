# Método de projeto — entrada única (ADR-121)

Procedimento de todo projeto conduzido com o framework: a ordem das etapas, o que sai de cada uma, onde mora e como
se verifica. Os demais guias continuam valendo e estão ligados na etapa em que servem. Caminhos relativos à raiz do
metacognition-framework.

## 1. Definições

| Termo | Definição |
|---|---|
| Especificação | Arquivo único `docs/specs/<projeto>/spec.md` (ADR-117), com as partes A a H |
| Área | Quem define as regras de negócio e aprova o processo (ex.: planejamento, qualidade) |
| Evidência | Arquivo que prova uma afirmação: consulta, extração, print, relatório; registrado no manifesto |
| Biblioteca | Conhecimento reutilizável da empresa (ADR-120): termos, consultas, fatos, runbooks |
| Gerado | Peça produzida por ferramenta a partir da especificação; nunca editada à mão |

## 2. Fluxo

| # | Etapa | Sai | Onde mora | Verificação |
|---|---|---|---|---|
| 0 | Abertura | trabalho registrado; perfil regulado e empresa declarados | `python tools/trabalhos.py registrar ...`; Parte A da especificação | `python tools/trabalhos.py listar` |
| 1 | Elicitação | respostas registradas; biblioteca consultada; escopo e prazo declarados | Parte A (dimensões de elicitação) | `python tools/check_spec_depth.py <spec.md>` |
| 2 | Confirmação da área | definições confirmadas com nome e data | planilha de confirmação (B3a-2) → Parte A | `**Requisitos confirmados por:**` preenchido |
| 3 | Especificação | requisitos, aceite, riscos, testes | Partes A, B, F, G | `check_completeness`, `check_field_mapping`; com impacto regulado, `python tools/regulado.py verificar <spec.md> --planejamento` |
| 4 | Desenho do processo | HTML de revisão e docx controlado | Parte H → `python tools/desenho_processo.py <spec.md> --out-dir <pasta>` | o gerador reprova passo solto, destino inexistente, mais de 15 passos sem macroação, desenho mais largo que a tela |
| 5 | Testes e evidências | resultado com evidência, nome e data | Parte G; manifesto `python tools/doc_intake.py evidencia registrar <arquivo> --manifesto <m.json> --origem "..." --liga "REQ-01"` | `python tools/doc_intake.py evidencia verificar <m.json>`; `python tools/regulado.py matriz <spec.md>` |
| 6 | Liberação | verificação completa; revisão isolada aprovada | Parte B ratificada; veredito em `_meta/qa/` | `python tools/regulado.py verificar <spec.md>` (sem `--planejamento`); `python tools/qa_evidence.py` |
| 7 | Operação e fechamento | conhecimento registrado; relatório; passagem | biblioteca (`docs/_private/conhecimento/`); `python tools/execution_report.py --from-transcripts`; `python tools/handoff.py` | `python tools/conhecimento.py verificar <raiz>`; `vencidos` |

## 3. Regras

1. Toda peça de auditoria sai de ferramenta a partir da especificação. Mudou a regra, muda a especificação e gera de
   novo.
2. Consultar a biblioteca antes de pesquisar e registrar nela ao fechar cada bloco (regra global, seção 9).
3. Conteúdo de evidência mudou: nome novo, e a versão anterior vai para `_obsoleto/` com o motivo no nome.
4. Arquivo com dado sensível fica fora do git e é marcado `--sensivel` no manifesto.
5. Não há perfil regulado padrão: o projeto declara o seu, ou "nenhum".
6. Cada bloco termina com revisão adversarial em subagente isolado de modelo diferente (regra global, seção 1).

## 4. Onde está o detalhe

- Primeira vez com o framework: `guia/POR-ONDE-COMECAR.md`. Equipe: `guia/GUIA-EQUIPE.md`.
- Mapeamento de processo (entrevista, SIPOC, RACI): `.agent/skills/discovery/mapeamento-de-processo.md`.
- Documentação do projeto graduada por porte: `_shared/project-docs/SKILL.md`.
- Termo de abertura (TAP): gerado pelo portal de projetos, fora do framework. Sem portal, a Parte D (Missão) da
  especificação cumpre o papel.
- Kit regulado: ADR-119. Biblioteca de conhecimento: `exemplos/conhecimento/_modelo/README.md`.
