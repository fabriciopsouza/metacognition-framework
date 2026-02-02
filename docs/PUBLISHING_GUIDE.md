# Guia Rápido: Publicar no GitHub

**Tempo estimado:** 15 minutos

---

## Pré-requisitos

1. **Ter conta no GitHub:** https://github.com/join
   - Username: `fabriciopsouza` (já configurado nos arquivos)
   
2. **Ter Git instalado:** 
   ```bash
   git --version
   ```
   Se não tiver: https://git-scm.com/downloads

3. **Configurar Git (primeira vez):**
   ```bash
   git config --global user.name "Fabricio Pinheiro Souza"
   git config --global user.email "fabriciopsouza@gmail.com"
   ```

---

## Passo 1: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name:** `metacognition-framework`
   - **Description:** `Universal prompt engineering framework for critical AI validation`
   - **Visibility:** Public
   - **NÃO marque:** "Add a README file" (já temos)
   - **NÃO marque:** "Add .gitignore" (já temos)
   - **License:** Choose a license → Creative Commons Attribution 4.0 International
3. Clique em **Create repository**

GitHub vai mostrar comandos. **IGNORE** (vamos usar nossos comandos abaixo).

---

## Passo 2: Inicializar Git Local

Abra terminal na pasta do repositório (a pasta `/mnt/user-data/outputs/metacognition-framework/` que receberá).

```bash
# Navegue até a pasta (ajuste o caminho se necessário)
cd /caminho/para/metacognition-framework

# Inicialize o repositório Git
git init

# Adicione todos os arquivos
git add .

# Faça o primeiro commit
git commit -m "feat: Initial release - Metacognition Framework v2.0

- Framework completo com validação de fontes
- Detecção de contexto adaptativa
- Exemplo de caso de uso (análise financeira)
- Documentação completa (README, CONTRIBUTING, LICENSE)
- Artigo técnico (em revisão)

Framework baseado em 25+ anos de experiência em BI/Analytics combinado com pesquisas MIT/NAACL sobre metacognição em LLMs."
```

---

## Passo 3: Conectar ao GitHub

```bash
# Renomear branch para 'main' (padrão GitHub)
git branch -M main

# Conectar ao repositório remoto (substitua 'fabriciopsouza' pelo seu username)
git remote add origin https://github.com/fabriciopsouza/metacognition-framework.git

# Enviar para GitHub (primeira vez)
git push -u origin main
```

**Autenticação:**
- GitHub vai pedir username e senha
- **Senha:** Use um **Personal Access Token** (não a senha da conta)
- Como criar token: Settings → Developer settings → Personal access tokens → Generate new token
- Permissões necessárias: `repo` (full control)

---

## Passo 4: Criar Release v2.0

No GitHub:

1. Acesse: https://github.com/fabriciopsouza/metacognition-framework/releases
2. Clique em **"Create a new release"**
3. Preencha:
   - **Tag version:** `v2.0.0`
   - **Release title:** `Metacognition Framework v2.0 - Source Validation Update`
   - **Description:**
     ```markdown
     ## 🎯 Destaques

     - ✅ Framework completo de metacognição para IAs
     - ✅ Validação de fontes de dados
     - ✅ Detecção automática de contexto
     - ✅ 5 etapas de validação crítica
     - ✅ Exemplo de caso de uso real

     ## 📚 Documentação

     - [README](./README.md) - Visão geral
     - [FRAMEWORK](./FRAMEWORK.md) - Framework completo
     - [Getting Started](./docs/GETTING_STARTED.md) - Tutorial passo-a-passo
     - [Exemplo](./examples/01_financial_analysis.md) - Caso de uso real

     ## 🔬 Origens

     Baseado em:
     - 25+ anos de experiência em BI/Analytics
     - Recursive Language Models (MIT CSAIL, 2025)
     - Metacognitive Prompting (NAACL 2024)

     ## 📝 Licença

     CC BY 4.0 - Use comercialmente, modifique, distribua com atribuição.
     ```
4. Clique em **"Publish release"**

---

## Passo 5: Configurar Topics (Tags)

No repositório GitHub:

1. Clique em **"⚙️ Settings"** (na página do repositório, não no perfil)
2. Vá até **"General"**
3. Na seção **"Repository name"** (topo), role até **"Topics"**
4. Clique em **"Add topics"**
5. Adicione (separados por espaço):
   ```
   prompt-engineering ai-validation llm chatgpt claude data-integrity business-intelligence metacognition quality-assurance data-science python
   ```
6. Save

---

## Comandos Git para Uso Futuro

### Fazer mudanças e atualizar GitHub

```bash
# 1. Ver o que mudou
git status

# 2. Adicionar arquivos modificados
git add .

# 3. Fazer commit (use mensagem descritiva)
git commit -m "docs: atualiza exemplo de análise financeira"

# 4. Enviar para GitHub
git push
```

### Ver histórico de commits

```bash
git log --oneline
```

### Criar nova branch para features experimentais

```bash
# Criar e mudar para nova branch
git checkout -b feature/nova-validacao

# Fazer mudanças, commit

# Enviar branch para GitHub
git push -u origin feature/nova-validacao

# Voltar para main
git checkout main
```

### Atualizar repositório local se mexeu no GitHub

```bash
git pull
```

---

## Troubleshooting

### "Permission denied (publickey)" ou erro de autenticação

**Solução:**
1. Use **HTTPS** (não SSH) como acima
2. Crie Personal Access Token: Settings → Developer settings → Tokens → Generate
3. Use token como senha quando Git pedir

### "Remote origin already exists"

**Solução:**
```bash
git remote remove origin
git remote add origin https://github.com/fabriciopsouza/metacognition-framework.git
```

### Quero desfazer último commit (ainda não dei push)

```bash
git reset --soft HEAD~1
```

### Quero desfazer mudanças em arquivo específico

```bash
git checkout -- nome_do_arquivo.md
```

---

## Checklist Final

Antes de divulgar o repositório:

- [ ] Repositório criado no GitHub
- [ ] Todos os arquivos enviados (git push)
- [ ] Release v2.0 criada
- [ ] Topics configurados
- [ ] README renderizando corretamente
- [ ] Todos os links funcionando
- [ ] LICENSE presente
- [ ] Nenhum dado sensível exposto

---

## Próximos Passos

Após publicar:

1. **Adicionar no LinkedIn:** Seção "Featured" → Add link → colar URL do repo
2. **Post de lançamento:** LinkedIn feed com link
3. **Compartilhar:** Grupos técnicos, Reddit (r/PromptEngineering)

---

**Boa sorte! 🚀**

Dúvidas: fabriciopsouza@gmail.com
