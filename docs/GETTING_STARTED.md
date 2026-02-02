# Getting Started com Metacognition Framework

**Tempo estimado:** 10 minutos

---

## Passo 1: Copiar o Framework

Abra o arquivo [`FRAMEWORK.md`](../FRAMEWORK.md) neste repositório.

Copie **TODO o conteúdo** do framework (são ~8.000 caracteres).

---

## Passo 2: Colar nas Configurações da IA

### ChatGPT

1. Acesse: Settings → Personalization → Custom Instructions
2. Cole o framework no campo **"How would you like ChatGPT to respond?"**
3. Save

### Claude

1. Acesse: Settings → Profile
2. Cole o framework no campo de instruções personalizadas
3. Save

### APIs (OpenAI, Anthropic, etc)

Use o framework como `system` prompt no payload:

```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_KEY")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="[COLAR TODO O FRAMEWORK AQUI]",
    messages=[
        {"role": "user", "content": "Sua pergunta aqui"}
    ]
)
```

---

## Passo 3: Testar

Abra **nova conversa** (importante: nova, não reusar antiga).

**Teste 1: Conversa Casual**
```
Você: Oi, tudo bem?
```
Esperado: Resposta natural, sem metacognição visível.

**Teste 2: Pergunta Simples**
```
Você: Quanto é 15% de 200?
```
Esperado: "30" (direto, sem decomposição).

**Teste 3: Análise Técnica**
```
Você: Calcule o ROI de um investimento de R$ 50.000 que retornou R$ 68.000 em 2 anos
```
Esperado: Resposta com [SOLUÇÃO], [CONFIANÇA], [VALIDAÇÕES], [FONTES], [RESSALVAS].

---

## Passo 4: Usar em Trabalho Real

Comece com tarefa de complexidade média:

**Exemplos bons para começar:**
- Calcular indicador financeiro com dados reais
- Criar script Python para processar CSV
- Analisar dataset com possíveis anomalias
- Desenvolver dashboard com fórmulas Tableau

**Evite começar com:**
- Perguntas casuais (framework não ativa)
- Tarefas muito simples (não precisa de validação)
- Brainstorming criativo aberto (sem critério de precisão)

---

## O Que Esperar

### Mudanças no Comportamento da IA

**Antes (sem framework):**
- Responde diretamente com confiança
- Não questiona premissas
- Não rastreia origem de dados
- Não explicita incertezas

**Depois (com framework):**
- Decompõe problema em etapas
- Explicita nível de confiança
- Valida lógica antes de entregar
- Rastreia fonte de cada número
- Identifica premissas ocultas
- PARA se detecta divergência

### Exemplo Real

**Pergunta:** "Crie um ETL Python para processar este CSV de 5 milhões de linhas"

**Resposta esperada (resumida):**

```
[SOLUÇÃO CLARA]
[código Python completo - sem placeholders]

[VALIDAÇÕES EXECUTADAS]
✓ Chunk processing (100k linhas) para não estourar memória
✓ Validação de tipos antes de processar
✓ Reconciliação: soma inputs = soma outputs
✓ Logging duplo para auditoria

[CONFIANÇA: ALTA (0,9)]

[RESSALVAS]
⚠️ Assumindo encoding UTF-8. Se for Latin1, adicionar: encoding='latin1'
⚠️ Missing values tratados como exclusão - confirmar regra de negócio

> ⚙️ Metacognição aplicada: validação de integridade + detecção de edge cases
```

---

## Troubleshooting

### "IA continua respondendo sem metacognição"

**Causa:** Framework não foi aplicado corretamente ou conversa antiga.

**Solução:**
1. Verificar se copiou TODO o framework
2. Abrir NOVA conversa (não reusar antiga)
3. Testar com pergunta técnica explícita

### "Respostas muito longas/verbosas"

**Causa:** IA está aplicando metacognição em contexto casual.

**Solução:**
- Framework tem detecção de contexto automática
- Se acontecer, inicie conversa com: "Resposta direta, sem validações"
- Ou pergunte coisas mais técnicas (framework é para isso)

### "Não entendo o formato [SOLUÇÃO] [CONFIANÇA]"

**Explicação:**
- É o formato estruturado do framework
- [SOLUÇÃO] = resposta ao seu pedido
- [CONFIANÇA] = quão certo a IA está (ALTA/MÉDIA/BAIXA)
- [VALIDAÇÕES] = verificações feitas
- [RESSALVAS] = avisos importantes

Você pode pedir: "Resuma isso em 2 linhas" se quiser versão curta.

---

## Próximos Passos

Após dominar o básico:

1. **Ver exemplos completos:** [`/examples/`](../examples/)
2. **Ler artigo técnico:** [`/case-study/ARTICLE.md`](../case-study/ARTICLE.md)
3. **Customizar framework:** Adicionar validações específicas do seu domínio
4. **Contribuir:** Compartilhar seus casos de uso

---

## Suporte

**Dúvidas?**
- Abra uma [Issue no GitHub](https://github.com/fabriciopsouza/metacognition-framework/issues)
- Contato: fabriciopsouza@gmail.com

**Framework não funcionou como esperado?**
- Descreva: (1) o que você pediu, (2) o que esperava, (3) o que recebeu
- Compartilhe via Issue para ajudarmos a melhorar

---

**Boa sorte! 🚀**
