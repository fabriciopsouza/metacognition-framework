---
name: output-format
description: "Núcleo SSoT do formato de entrega e da validação obrigatória. Carregar antes de entregar qualquer fórmula, cálculo, código, visualização ou modelo. Define os templates de saída por modo e o checklist único de validação (edge cases, DIV/0, NULL, agregação). NÃO carregar para conversa casual."
version: 1.0.0
source: "master v4.1 §9 e §10 + metacognição v2.2 §3 + SQUAD v1.1.0 (developer/qa-critic/bi-deliverable)"
last_review: 2026-05-23
---

# Formato de Saída e Validação — Fonte Única

## Parte A — Formato por modo

**Casual / factual:** resposta direta, sem tags, sem cabeçalho. Anti-alucinação
em modo silencioso.

**Metacognição (tarefa pontual):**
```
[ENTENDIMENTO] reformulação do pedido em 1-2 frases
[ABORDAGEM]    método proposto
[SOLUÇÃO]      código/fórmula/explicação
[VALIDAÇÃO]    edge cases testados, premissas, ressalvas
[CONFIANÇA]    classificação por afirmação relevante
```

**Squad (por papel):**
```yaml
papel: <pmo|architect|developer|qa-critic|docops|explorer>
classificacao: [CONFIRMADO|INFERIDO|DESCONHECIDO]
fontes_consultadas: [arquivos/docs lidos]
artefatos: [paths gerados/alterados]
proximos_passos: [...]
escalacoes: [...]
```

Anti over-formatting: sem ASCII boxes; emojis só com função semântica
(⚠️ alerta, 🛑 stop, 📍 checkpoint); listas só com ≥3 itens paralelos;
tabelas só quando comparam algo de fato.

## Parte A.0 — O texto se sustenta sozinho (vale para CONVERSA, não só para arquivo)

**Regra:** quem lê entende **na primeira leitura, sem abrir outro arquivo e sem
conhecer o projeto.** Código interno, número de decisão e referência cruzada podem
aparecer — e devem, porque é por eles que se **confere** uma afirmação. Mas eles
são **apoio à verificação, nunca o caminho para a compreensão**.

Isto **não** é a mesma exigência de "explicar o jargão na primeira aparição"
(`project-docs` §2.6). Aquela é mais fraca: é possível explicar cada sigla e ainda
escrever um texto que só faz sentido para quem acompanhou a conversa anterior.
Aqui a régua é o entendimento do texto inteiro, não a definição dos termos.

**Onde vale:** em toda entrega **e em toda resposta de conversa**. Este é o ponto
que faltava: sem ele o agente produz documento legível e conversa cifrada, porque
só o documento tinha régua. Registro técnico continua técnico e fundamentado — a
régua muda a **redação**, nunca o rigor.

### Os quatro defeitos que reprovam, com o antes e o depois

**1. Referência cifrada no lugar da explicação.** `"B0 contradiz §7, segundo P1"`
não informa: obriga o leitor a abrir três arquivos para descobrir se aquilo é bom
ou ruim. Escreva o que está em conflito e qual a consequência; depois cite a fonte
entre parênteses, para quem quiser conferir.

**2. Adjetivo que esconde o sujeito.** *"a precisão perdida é invisível"* — invisível
**a quem**, e quando essa pessoa descobre? Do jeito que está, o leitor pode
entender o contrário do pretendido: que não há impacto.

> Antes: *"o arquivo de exclusão engolia a documentação em silêncio."*
> Depois: *"o Git não avisava nada: o `git status` aparecia limpo e o envio
> funcionava. Só quem fosse abrir a documentação depois — dias depois —
> descobriria que ela nunca chegou ao repositório."*

O depois diz **quem** não percebe, **quando** descobre e **qual** o dano. Palavras
como *invisível*, *silencioso* e *em silêncio* só entram acompanhadas dessas três
coisas na mesma frase.

**3. Nome do mecanismo no lugar do efeito.** *"aplica-se `G-06`"* não permite
decidir nada. *"a automação não repete uma ação já feita, e confere que ela
aconteceu antes de dizer que deu certo (padrão `G-06`)"* permite.

**4. Conclusão sem consequência.** Achado sem dizer o que muda para quem decide é
relatório, não informação. Toda afirmação relevante responde: e daí?

### Como conferir

Leia a própria entrega **como se não tivesse participado da conversa**. Toda vez
que precisar de contexto externo para entender uma frase, essa frase reprova.

Quando houver artefato gerado por ferramenta, a checagem sai da cabeça e vira
comando — a instância de referência é o gate que reprova código citado no texto e
ausente da tabela que o explica, em
`copiloto-automacoes-sap/tools/novo_processo.py` (`validar --so-marcas`).

**Débito declarado:** para conversa não existe gate — é prosa, e prosa é débito
(Parte A.1). Não há mecanismo que inspecione a resposta antes de ela sair. O que
existe é a cobrança do dono na revisão, e este texto para que a cobrança tenha
onde se apoiar. Quitação: se um dia houver hook de fim-de-turno, esta régua é
candidata a virar checagem automática.

## Parte A.1 — Determinismo-primeiro × prosa-pela-porta (P15 — ADR-085)

Antes de entregar QUALQUER capacidade que **decide ou produz artefato**: o mecanismo é **determinístico** (tool + canário fail-closed) sempre que alcançável. Prosa/template/parada-e-orientação é fallback **só pela PORTA**: (a) o julgamento é **irredutível** E (b) está provado que a ferramenta **não captura**. Fora disso, prosa = débito (`enforcement: prose` no `capabilities.json`), não solução.

Declarar, por capacidade: `{parte determinística | parte prosa-pela-porta | fallback stop-and-guide}`. **Lar canônico da declaração:** o campo `enforcement` de cada registro em `capabilities.json` (`fail-closed`/`physical` = determinístico; `prose`/`fail-soft` = débito visível na lista "débito-mecanização" do `tools/test_capabilities.py`) — não se repete a declaração em cada SKILL.md. A **parada-e-orientação** (parar o fluxo e pedir a decisão ao humano em vez de adivinhar) é o fallback canônico — **determinística na forma** (é um gate), prosa só no conteúdo da decisão; é **degradação graciosa, não duplicata** (não-incho). Não é só de uma skill: vale para todo skill/tool/gate (núcleo uma vez, referenciado — nunca copiado).

## Parte B — Checklist único de validação (antes de entregar)

**Técnico**
- [ ] Sintaxe sem erro (linter / compilador / checagem da ferramenta)
- [ ] Tipos consistentes; conversão explícita antes de lógica numérica
- [ ] NULL tratado (`IFNULL`/`ZN`/`try/except`)
- [ ] DIV/0 tratado (`ZN`, `DIVIDE`, `IIF` com guard, `IFERROR`)
- [ ] Edge cases: zero, NULL, negativo, extremo, string vazia
- [ ] Agregação no nível correto (sem mix AGG/non-AGG)

**Lógico**
- [ ] Resultado em ordem de magnitude esperada
- [ ] Cross-check com fonte alternativa quando possível
- [ ] Reconciliação Total = Soma das Partes (quando aplicável)
- [ ] Premissas explícitas

**Visual (quando aplicável)**
- [ ] Título + subtítulo com guia de leitura inline (ex.: `BARRA=Real | ◆=Meta`)
- [ ] Cores acessíveis; eixos com range apropriado
- [ ] Aspect ratio igual em scatter/quadrante

**Test cases obrigatórios** para fórmula/cálculo crítico: tabular Normal / Zero /
NULL / Negativo / Extremo com input, esperado, resultado, status.
