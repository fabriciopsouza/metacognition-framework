# Biblioteca de conhecimento do dono (instância)

Local definido pelo plano B3, decisão D9: `docs\_private\conhecimento\`, fora das distribuições públicas.
Estrutura, formato e método: `exemplos\conhecimento\_modelo\README.md` (ADR-120).

- **Conteúdo** (termos, consultas, fatos, pesquisas, runbooks de cada empresa): registrado pelas sessões de domínio,
  no ato, conforme o método. Esta pasta nasce vazia de conteúdo.
- **Verificar uma empresa:** `python tools\conhecimento.py verificar docs\_private\conhecimento --empresa <empresa>`
  (dentro da pasta de um projeto do índice, `--empresa` pode ser omitido).
- **Manutenção da biblioteca inteira:** `python tools\conhecimento.py verificar docs\_private\conhecimento --empresa todas --trabalhos %USERPROFILE%\.claude\trabalhos`
  (só aqui a checagem com `--trabalhos` acusa projeto de domínio com trabalho aberto e sem linha no índice).
- **Buscar:** `python tools\knowledge_catalog.py --recall --context "<termos>" --conhecimento docs\_private\conhecimento --empresa <empresa>`
- **Isolamento entre empresas:** o conhecimento de uma empresa nunca aparece no trabalho de outra; saber puro de
  assunto vai para `assuntos\<assunto>\` (método no README do modelo, seção 2).
- **Bibliotecas das empresas (27/09/2026):** fora deste repositório, em `C:\Users\fabriciosouza\conhecimento-negocio\`
  (repositório privado `conhecimento-negocio`, um submódulo por empresa; aqui, só o da empresa desta máquina).
  - Natulab: `empresas\natulab` = `conhecimento-natulab`.
  - Registrar conhecimento: commit dentro do submódulo, depois atualizar o ponteiro no pai.
  - Mudou `## Identificadores` ou o índice da empresa:
    `python tools\conhecimento.py publicar docs\_private\conhecimento --empresa <empresa>` e commit aqui.
