# Como o método foi construído

> **Regra deste documento (a mesma do framework): só a verdade.** Sem exagero, sem megalomania.
> Onde a evidência é fina, está dito. As **falhas** estão aqui — porque é delas que o método melhora.

O Framework Metacognitivo Agêntico não nasceu de teoria. Foi **destilado de pesquisa**, **construído por
dogfooding** (o framework se aplica a si mesmo) e **endurecido por falhas reais**.

---

## 1. Fundamento — pesquisa, não opinião

Cada decisão é ancorada em fonte, não em achismo:
- **Publicações de engenharia da Anthropic:** *Building effective agents*, *Effective context engineering*,
  *multi-agent research system*, *Agent Skills*.
- **Padrões abertos:** SemVer, Keep a Changelog, ADR/MADR, OWASP Top 10 for LLM Applications, OpenTelemetry GenAI.
- **Quatro estudos internos (A0–A3):** fundamentos de contexto; RAG multiagente em produção; desenvolvimento
  com agentes (spec-driven); governança de IA não-determinística em ambiente regulado.

Bibliografia completa e classificada: [`REFERENCIAS.md`](REFERENCIAS.md). Cada release vincula a mudança à
fonte que a sustenta no [`CHANGELOG.md`](../CHANGELOG.md).

## 2. Construção — dogfooding e decisões rastreáveis

O framework é desenvolvido **sob as próprias regras**: cada mudança passa por
discovery → architect → **ADR** (decisão registrada) → developer → **qa-critic adversarial** → docops.
São **23 ADRs** (decisões com pergunta, alternativas e porquê) e versionamento SemVer com CHANGELOG.
Não há mudança "porque sim" — há um registro do *como se chegou ali*.

## 3. Validação — o que é medido (sem inflar)

O que existe **de fato**, hoje:
- **Roteamento dos papéis operacionais testado 33/33** (papéis A–F do conjunto de avaliação; o roteamento do `discovery` tem casos escritos mas em *design-time*, execução pendente — declarado, não inflado).
- **Hooks de runtime com testes-canário que TENTAM furá-los** (effect-gate, compaction-gate, mission-gate) —
  e que falham o build se um caso passar errado.
- **QA adversarial heterogêneo** (modelo de família diferente do que gerou) em cada bloco entregue.
- **Um caso real, regulado:** um recálculo com *baseline golden* (REQ-001..011 entregues), validado com
  **delta 0.000000** contra o baseline — ou seja, saída idêntica à referência aprovada, medida.

> **O que NÃO afirmamos (honestidade explícita):** não há benchmark contra frameworks alternativos, não há
> números de adoção, nem reconhecimento externo/prêmios. Nomes de clientes não são publicados aqui (confidencialidade).
> A prova disponível é: dogfooding + validação interna + um caso real medido. **Para o seu contexto, valide você.**

## 4. As falhas — porque a honestidade É o método

Um método que esconde falha não é confiável. Estas são reais, registradas no `history.md ## Aprendizado`:

**O QA adversarial PEGOU (antes de publicar):**
- **Bug de contrato ALTO (v1.21.0):** um hook de produto exigia um formato que o template não mostrava —
  o estado de sucesso era *inalcançável pelo caminho documentado*. **Três testes verdes escondiam o bug**
  (foram escritos com o mesmo ponto-cego de quem fez o código); o crítico em **modelo heterogêneo** pegou.
- **Overclaim de segurança ALTO:** uma versão deste material afirmava que um gate rodava "por default"
  quando ele **não estava instalado**. O crítico exigiu a correção antes de ir ao ar.

**O QA NÃO pegou — o DONO (humano) pegou:**
- **Vazamento de norma de domínio no núcleo (≥2×):** termos de norma regulatória entraram onde o núcleo
  deveria ser agnóstico. A auto-observação do agente **racionalizou** e não detectou; o dono viu. **Solução:**
  um *linter executável* de agnosticismo (ADR-020) — a prosa virou mecanismo.
- **Viés "processo sobre produto":** o agente otimizou o rigor do processo e subvalorizou a **entrega de produto**.
  O dono reorientou; virou a camada de entrega (ADR-023).

**Falhas operacionais (e o que viraram):**
- Uma sessão operou **41 commits atrás** do main por não sincronizar → virou hook `check-repo-sync` (ADR-019).
- Um PR foi **mergeado cedo**, antes de commits de documentação → virou a política **"parar no PR, merge é gate humano"**.

## 5. A lição recorrente: prosa → mecanismo

O padrão por trás de quase toda falha: uma regra que existia **só como texto** e dependia de boa-vontade.
A solução, repetida: dar a cada regra crítica um **par executável com teste que tenta furá-la**. É por isso
que o método melhora com o tempo — **as falhas viram mecanismos**, não viram desculpas. E a defesa final
contra o ponto-cego do próprio agente é dupla: **gate humano** + **revisor em modelo diferente**.

---

> Quer aprofundar? As decisões estão em [`docs/adr/`](../docs/adr), o histórico honesto (incluindo a seção
> `## Aprendizado`) no [`history.md`](../history.md), e a base de evidência em [`REFERENCIAS.md`](REFERENCIAS.md).
