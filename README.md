# Metacognitive Recursion Framework for AI
**A Universal Prompt Engineering Framework for Critical Validation and Reasoning**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/fabriciopsouza/metacognition-framework)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 🎯 O Problema

A maioria das interações com LLMs segue o padrão: pergunta → resposta → confiança cega no resultado.

**Isso funciona para conversas casuais.** Para trabalho crítico — análises de dados, desenvolvimento de código, cálculos financeiros — esse padrão gera:

- ❌ Cálculos incorretos apresentados com confiança
- ❌ Código com bugs sutis não detectados
- ❌ Análises baseadas em premissas erradas
- ❌ Retrabalho custoso após stakeholders identificarem erros

**Por quê?** LLMs não validam raciocínio por padrão. Não questionam premissas. Não rastreiam origem de dados. Não explicitam nível de confiança.

---

## 💡 A Solução

Framework de **Metacognição Recursiva** que força o LLM a:

1. **Decompor** problemas complexos em partes verificáveis
2. **Resolver** cada parte com nível de confiança explícito
3. **Verificar** lógica, dados e premissas antes de entregar
4. **Sintetizar** usando confiança ponderada
5. **Refletir** e propor validações se confiança < 80%

**Diferencial crítico:** Se detectar divergências em cálculos, **PARA** e solicita confirmação antes de apresentar resultado.

---

## 🔬 Origens do Framework

Este framework combina:

### Pesquisas Acadêmicas Recentes
- **Recursive Language Models** (MIT CSAIL, 2025) — paradigma de inferência que trata prompts longos como ambiente externo [1]
- **Metacognitive Prompting** (NAACL 2024) — técnicas para LLMs refletirem sobre próprio raciocínio [2]
- **Chain-of-Thought with Self-Consistency** — múltiplas perspectivas para validar raciocínio [3]

### Experiência Profissional (25+ anos)
- **Business Intelligence & Analytics** — validações duplas em análises financeiras, reconciliação obrigatória
- **ETL e Data Pipelines** — integridade de dados em cada etapa, rastreabilidade completa
- **Desenvolvimento de indicadores corporativos** — precisão crítica em KPIs, zero tolerância a erros

### Casos de Uso Reais Testados
- Análises financeiras com valores críticos (~R$ 100M+)
- ETLs processando milhões de registros com validação linha a linha
- Dashboards executivos onde cada número precisa ter fonte rastreável
- Produção musical com parâmetros técnicos específicos
- Desenvolvimento de código crítico

---

## 🚀 Resultados Observados

**Redução de Erros:**
- Retrabalho por erros em cálculos: redução significativa (>60%)
- Bugs em código: detecção precoce de edge cases
- Análises baseadas em premissas erradas: identificadas antes de reportar

**Ganho de Eficiência:**
- Validações manuais (horas) → automatizadas (minutos)
- 100% de rastreabilidade em análises críticas
- Detecção antecipada de problemas

**Melhoria de Confiança:**
- LLM admite quando não tem certeza (confiança < 80%)
- Explicita premissas ocultas
- Oferece múltiplas perspectivas em decisões estratégicas

---

## 📋 Como Usar

### Instalação

1. **Copie o framework** do arquivo [`FRAMEWORK.md`](./FRAMEWORK.md)

2. **Cole nas configurações da sua IA:**
   - **ChatGPT:** Settings → Personalization → Custom Instructions
   - **Claude:** Settings → Profile (campo de instruções personalizadas)
   - **APIs:** Use como `system prompt` no payload

3. **Teste em nova conversa:**
   ```
   Calcule o ROI de um investimento de R$ 50.000 que retornou R$ 68.000 em 2 anos
   ```

   Esperado: resposta com [SOLUÇÃO], [CONFIANÇA], [VALIDAÇÕES], [FONTES], [RESSALVAS]

### Exemplos de Uso

Ver [`examples/`](./examples/) para casos completos com transcrições.

---

## 📁 Estrutura do Repositório

```
metacognition-framework/
├── README.md                    # Este arquivo
├── FRAMEWORK.md                 # Framework completo
├── LICENSE                      # CC BY 4.0
├── examples/                    # Casos de uso com transcrições
│   └── 01_financial_analysis.md
├── case-study/                  # Artigo técnico
│   └── ARTICLE.md
└── docs/                        # Guias complementares
    ├── GETTING_STARTED.md
    └── PUBLISHING_GUIDE.md
```

---

## 🎯 Quando Usar

✅ **Use este framework quando:**
- Trabalhar com dados financeiros/críticos
- Desenvolver código que vai para produção
- Criar análises para stakeholders
- Processar pipelines de dados (ETL)
- Produzir conteúdo técnico especializado
- Qualquer situação onde erro custa caro

❌ **Não precisa usar quando:**
- Conversas casuais
- Perguntas factuais simples
- Brainstorming criativo sem precisão crítica

---

## 📚 Referências

[1] Zhang, A. L., Kraska, T., & Khattab, O. (2025). *Recursive Language Models*. arXiv:2512.24601. MIT CSAIL.

[2] Didolkar, A., et al. (2024). *Metacognitive Prompting Improves Understanding in Large Language Models*. NAACL 2024.

[3] Wang, X., et al. (2023). *Self-Consistency Improves Chain of Thought Reasoning in Language Models*. ICLR 2023.

[4] CFA Institute. (2021). *Investment Performance Measurement*. CFA Institute Research Foundation.

[5] Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit* (3rd ed.). Wiley.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Especialmente:

- Novos casos de uso com transcrições
- Validações específicas de domínio
- Traduções para outras línguas
- Melhorias no framework

Ver [CONTRIBUTING.md](./CONTRIBUTING.md) para guidelines.

---

## 📄 Licença

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

Você pode usar comercialmente, modificar, distribuir e usar privativamente.

**Requisito:** Dar crédito apropriado ao autor original.

Atribuição sugerida:
```
Metacognitive Recursion Framework
Autor: Fabricio Pinheiro Souza
Repositório: https://github.com/fabriciopsouza/metacognition-framework
Licença: CC BY 4.0
```

---

## 👤 Autor

**Fabricio Pinheiro Souza**  
Senior Data Analyst | 25+ anos em BI/Analytics  

📧 Contato: fabriciopsouza@gmail.com  
🔗 LinkedIn: [linkedin.com/in/fabriciopinheirosouza](https://www.linkedin.com/in/fabriciopinheirosouza/)  
💻 GitHub: [@fabriciopsouza](https://github.com/fabriciopsouza)

---

## 📊 Status do Projeto

- [x] Framework v1.0 - Lançamento inicial
- [x] Framework v2.0 - Validação de fontes de dados
- [ ] Casos de uso documentados (1/5)
- [ ] Traduções (EN, ES)
- [ ] Extensões por domínio
- [ ] API wrapper para automação

---

**Última atualização:** 02/02/2025  
**Versão:** 2.0
