# PITCH & Divulgação — textos prontos para usar

> Peças de copy para apresentar o Framework Metacognitivo Agêntico como **produto**.
> Tom: proposta de **valor por resultado**, honesto. Licença CC BY 4.0 (livre) — "vender" aqui
> é **fazer adotar**, não cobrar. **Sem métrica inventada:** o único número factual é a cobertura de
> testes do roteamento de papéis (33/33) e os testes-canário dos hooks; não prometa benchmark que
> não temos. Copie, adapte ao canal, credite.

---

## 1. Tagline (uma linha — escolha por canal)

- **Curta:** Orquestre agentes de IA que não alucinam, não esquecem, e entregam produto.
- **Direta:** O método que faz o agente dizer "não sei" — e terminar em código, não em prosa.
- **Técnica:** Um núcleo flexível de orquestração: confiança classificada, memória cross-sessão, QA adversarial e enforcement em runtime.
- **Provocativa:** Pare de revisar a alucinação do seu agente. Mude o método.

---

## 2. Elevator pitch (~30s)

> Todo mundo já viu um agente de IA afirmar com confiança um nome de campo que não existe, esquecer
> o que foi decidido quando o contexto enche, ou produzir três parágrafos lindos e nenhum código que
> roda. O **Framework Metacognitivo Agêntico** é um método de orquestração que ataca isso na raiz:
> o agente **classifica o que sabe** (confirmado / inferido / não sei) e nunca inventa; **grava um
> digest antes de compactar**, então a próxima sessão começa sem perguntar nada; passa por um **revisor
> adversarial independente** que assume que existe bug; e **culmina em produto** — software ou dados
> entregáveis. É flexível: adapta-se ao seu contexto e ao seu código atual, sem forçar refatoração.
> Roda no Claude Code, é open source (CC BY 4.0), e cada regra crítica tem um hook que a faz valer
> em runtime — não é promessa, é mecanismo.

---

## 3. Problema → Solução (bloco curto, para landing/deck)

**O problema.** Agentes soltos alucinam fatos, esquecem contexto ao compactar, incham com cerimônia
que ninguém usa, e param na conversa. "Confio no shell" vira a porta para um `rm -rf` irreversível.

**A solução.** Um núcleo que torna o agente **honesto** (classifica toda afirmação), **com memória**
(digest persistente entre sessões), **enxuto** (adição pura é rejeitada — só entra o que funde, remove
ou destrava), **seguro** (gate por efeito bloqueia o irreversível) e **produtivo** (entrega artefato,
não prosa). Tudo agnóstico de domínio: o mesmo núcleo serve dev, dados, BI ou contexto regulado.

---

## 4. Post para LinkedIn

> Seu agente de IA já te entregou, com toda a confiança do mundo, um nome de coluna que não existe?
>
> O problema raramente é o modelo. É a **falta de método** em volta dele.
>
> Passei [tempo] construindo um framework de orquestração que ataca os 4 modos de falha que mais doem:
>
> 🎯 **Alucinação** → toda afirmação é classificada: confirmado, inferido, ou "não sei" (dito direto).
> 🧠 **Amnésia** → digest persistente antes de compactar; a próxima sessão começa sem perguntar nada.
> 🪶 **Inchaço** → adição pura é rejeitada por padrão; só entra o que reduz custo ou destrava.
> 📦 **Prosa sem produto** → o fluxo termina em software/dados entregáveis, conforme o briefing.
>
> E o detalhe que mais me orgulha: as regras críticas não ficam só no texto. Viram **hooks executáveis
> com testes que tentam furá-las**. Da prosa ao mecanismo.
>
> É open source (CC BY 4.0), roda no Claude Code, e é agnóstico de domínio.
>
> 👉 [link]
>
> #IA #Agentes #AIengineering #ClaudeCode #LLM

---

## 5. Thread curto (X/Twitter)

1/ Seu agente de IA não tem um problema de inteligência. Tem um problema de **método**. 🧵

2/ Ele alucina porque ninguém o obrigou a classificar o que sabe. Solução: todo fato é confirmado,
   inferido, ou "não sei". Sem meio-termo. Sem invenção.

3/ Ele esquece porque o contexto é finito e a compactação apaga decisões. Solução: digest persistente
   antes de compactar — a próxima sessão começa sem perguntar nada.

4/ Ele incha porque "mais agente = melhor" é mito. Solução: adição pura é rejeitada. Só entra o que
   funde, remove ou destrava.

5/ Ele para na conversa. Solução: o fluxo **culmina em produto** — código, app, notebook, pipeline.

6/ E nada disso fica só no texto: regra crítica vira **hook executável com teste que tenta furá-la**.

7/ Open source, CC BY 4.0, roda no Claude Code, agnóstico de domínio. 👉 [link]

---

## 6. Hero para o topo do README (alternativa de gancho)

> **Framework Metacognitivo Agêntico** — orquestre agentes que classificam o que sabem, lembram entre
> sessões, recusam inchar, e culminam em produto. Um método flexível (não um framework rígido) sobre
> Claude Code: cada regra crítica tem um hook que a faz valer em runtime. CC BY 4.0.

---

## 7. Três bullets de valor (para deck/site)

- **Honestidade por padrão.** O agente diz "não sei" e classifica cada afirmação — você para de caçar alucinação depois.
- **Continuidade real.** Memória cross-sessão: decisões, nomes e pendências sobrevivem ao reset de contexto.
- **Termina em entrega.** Não é um chatbot que opina; é um pipeline que entrega artefato validado conforme o briefing.

---

## 8. Mini-FAQ (objeções comuns)

- **"É mais um wrapper de prompt?"** Não. É método + enforcement: hooks executáveis com testes,
  contrato de papéis validado em CI, gate de ações destrutivas por efeito. A regra não depende de boa-vontade.
- **"Vai me forçar a refatorar tudo?"** Não. Atua por atualização e melhoria dirigida; só muda o que
  você aprova, declarando o que sai/fica/entra.
- **"Serve pro meu domínio?"** Sim — o núcleo é agnóstico. O domínio (linguagem, norma, regra de
  negócio) é declarado por projeto e vive fora do núcleo. Escala por clonagem.

---

> **Regra de honestidade (não-negociável, espelha o próprio framework):** nenhuma peça acima deve
> alegar número, benchmark ou cliente que não exista. Resultado factual disponível hoje: roteamento
> de papéis testado 33/33 + testes-canário dos hooks de runtime. O resto é proposta de valor, não dado.
