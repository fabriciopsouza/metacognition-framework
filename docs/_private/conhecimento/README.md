# Biblioteca de conhecimento do dono (instância)

Local definido pelo plano B3, decisão D9: `docs\_private\conhecimento\`, fora das distribuições públicas.
Estrutura, formato e método: `exemplos\conhecimento\_modelo\README.md` (ADR-120).

- **Conteúdo** (termos, consultas, fatos, pesquisas, runbooks de cada empresa): registrado pelas sessões de domínio,
  no ato, conforme o método. Esta pasta nasce vazia de conteúdo.
- **Verificar:** `python tools\conhecimento.py verificar docs\_private\conhecimento --trabalhos %USERPROFILE%\.claude\trabalhos`
  (enquanto o índice estiver vazio, a checagem com `--trabalhos` acusa cada projeto de domínio com trabalho aberto:
  é a pendência de preenchimento, não defeito).
- **Buscar:** `python tools\knowledge_catalog.py --recall --context "<termos>" --conhecimento docs\_private\conhecimento`
