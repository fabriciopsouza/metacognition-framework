# Método de projeto — entrada única (ADR-121)

Procedimento de todo projeto conduzido com o framework: a ordem das etapas, o que sai de cada uma, onde mora e como
se verifica. Os demais guias continuam valendo e estão ligados na etapa em que servem. Caminhos relativos à raiz do
metacognition-framework.

## 1. Definições

| Termo | Definição |
|---|---|
| Especificação | Arquivo único `docs/specs/<projeto>/spec.md` (ADR-117), com as partes A a J |
| Área | Quem define as regras de negócio e aprova o processo (ex.: planejamento, qualidade) |
| Evidência | Arquivo que prova uma afirmação: consulta, extração, print, relatório; registrado no manifesto |
| Biblioteca | Conhecimento reutilizável da empresa (ADR-120): termos, consultas, fatos, runbooks |
| Gerado | Peça produzida por ferramenta a partir da especificação; nunca editada à mão |

## 2. Fluxo

| # | Etapa | Sai | Onde mora | Verificação |
|---|---|---|---|---|
| 0 | Abertura | trabalho registrado; perfil regulado e empresa declarados | `python tools/trabalhos.py registrar ...`; Parte A da especificação | `python tools/trabalhos.py listar` |
| 1 | Elicitação | respostas registradas; biblioteca consultada; escopo e prazo declarados | Parte A (dimensões de elicitação) | `python tools/check_spec_depth.py <spec.md>` |
| 2 | Confirmação da área | definições confirmadas com nome e data | Parte I e pontos da Parte H → `python tools/planilhas_projeto.py gerar <spec.md> --out-dir <pasta>` (`confirmacao_vN.xlsx`); resposta de volta com `importar <spec.md> --planilha <xlsx> --out-dir <pasta>`. Rótulos do cabeçalho adaptados ao domínio em `### Rótulos` | `python tools/planilhas_projeto.py situacao <spec.md> --exigir` (toda definição e ponto com "Sim", nome e data); então `**Requisitos confirmados por:**` preenchido |
| 3 | Especificação | requisitos, aceite, riscos, testes | Partes A, B, F, G | `check_completeness`, `check_field_mapping`; com impacto regulado, `python tools/regulado.py verificar <spec.md> --planejamento` |
| 4 | Desenho do processo | HTML de revisão e docx controlado | Parte H → `python tools/desenho_processo.py <spec.md> --out-dir <pasta>` | o gerador reprova passo solto, destino inexistente, mais de 15 passos sem macroação, desenho mais largo que a tela |
| 5 | Testes e evidências | resultado com evidência, nome e data; conferência da área no sistema | Parte G; Parte J → `verificacao_vN.xlsx` pelo mesmo `planilhas_projeto.py`; nova volta com a área: `planilhas_projeto.py rodada <spec.md> --data dd/mm/aaaa --ids VER-nn`; manifesto `python tools/doc_intake.py evidencia registrar <arquivo> --manifesto <m.json> --origem "..." --liga "REQ-01"` | `python tools/doc_intake.py evidencia verificar <m.json>`; `python tools/regulado.py matriz <spec.md>` |
| 6 | Liberação | verificação completa; revisão isolada aprovada; documentos do perfil (ex.: requisitos, relatório de validação, prontidão) e mudança e versão gerados | Parte B ratificada; veredito em `_meta/qa/`; `python tools/regulado.py documento <tipo> <spec.md> --out-dir <pasta>`; `python tools/mudancas_spec.py <spec.md> --out-dir <pasta>` | `python tools/regulado.py verificar <spec.md>` (sem `--planejamento`); `python tools/qa_evidence.py` |
| 7 | Operação e fechamento | conhecimento registrado; relatório; passagem | biblioteca (`docs/_private/conhecimento/`); `python tools/execution_report.py --from-transcripts`; `python tools/handoff.py` | `python tools/conhecimento.py verificar <raiz> --empresa <empresa>`; `vencidos` |

## 3. Regras

1. Toda peça de auditoria sai de ferramenta a partir da especificação. Mudou a regra, muda a especificação e gera de
   novo.
2. Consultar a biblioteca antes de pesquisar e registrar nela ao fechar cada bloco (regra global, seção 9).
3. Conteúdo de evidência mudou: nome novo, e a versão anterior vai para `_obsoleto/` com o motivo no nome.
   Planilha para a área: cada gravação é vN+1; a anterior só é apagada depois de o gerador comparar as respostas.
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
