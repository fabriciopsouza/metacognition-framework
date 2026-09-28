# ADR-126 — Perfil farma-anvisa: leitura primária e mapa peça → norma

- **Status:** Aceito
- **Data:** 2026-09-28
- **Decisores:** dono (Fabricio):
  - 27/09/2026: o perfil ANVISA é de aplicação e nunca cita empresa; depois virão ANP e outros;
  - 28/09/2026: "vamos começar com o que temos: medicamentos. Depois será ANP, não alimentos"; "D2 farma" (mantém o nome `farma-anvisa`).

  Autoria: Opus 5.5.
- **Relação:** executa o B3b (T6) do plano `docs/specs/b3-documentacao-regulada/spec.md`. Usa o motor neutro do
  ADR-119 e os documentos do ADR-124.

## Contexto
As citações de artigo do perfil estavam marcadas INFERIDO. A IN 134 e a IN 138 tinham sido trianguladas em fontes
secundárias, sem leitura do texto oficial. O perfil não dizia de qual artigo vinha cada peça exigida. Nenhuma
ferramenta conferia isso.

## Decisão
1. **Leitura primária em 28/09/2026:** textos integrais da IN 134/2022, da IN 138/2022, da RDC 658/2022, da RDC
   972/2025 e do Guia 33/2020, com conferência no DOU. Vigência, URLs e divergências estão em
   `docs/specs/b3-documentacao-regulada/fontes.md`, seção 6.
2. **Mapa `exemplos/dominio-regulado/farma-anvisa-mapa-normas.md`:** cada linha liga uma peça do perfil a uma norma e
   um artigo, com o trecho literal e a marca de confiança. Toda linha com norma citada está CONFIRMADO; nenhuma
   ficou INFERIDO ou DESCONHECIDO. As peças de gestão do projeto levam a marca NÃO SE APLICA. O schema do perfil não foi estendido.
3. **`python tools/regulado.py mapa <perfil.json>`:** todo perfil com `categorias_software` precisa do mapa
   `<profile>-mapa-normas.md` ao lado. Reprova quando:
   - uma peça do perfil está sem linha no mapa;
   - uma linha fala de peça que o perfil não tem;
   - a marca de confiança é inválida;
   - uma linha citada está sem norma ou sem artigo.

   Vale para os próximos perfis (ANP) sem mudar o motor, que continua sem nome de norma.
4. **Perfil corrigido pelo texto da norma:**
   - só medicamentos;
   - trilha de auditoria "por risco" (IN 134, art. 33, "deve ser considerada");
   - assinatura eletrônica "quando usada" (art. 41, "podem ser assinados");
   - a categoria de software (GAMP) declarada como escalonamento do Guia 33, não vinculante;
   - a sigla ALCOA+ declarada ausente do texto oficial.

## Régua §0
Critério (c): a base normativa das peças deixa de ser prosa e passa a ser conferida pelo canário. Estende a
capacidade `kit-regulado`, sem registro novo: 1 comando e 1 arquivo de dados.

## Limites
- **O verificador confere a forma**, não o conteúdo: uma linha com artigo errado e marca CONFIRMADO passa. A
  conferência do trecho com a norma é da revisão adversarial e da Qualidade.
- **Andaime, não certificação:** a norma aplicável e o código de documento controlado continuam vindo da Qualidade
  da empresa.

## Prova
- `tools/test_regulado.py` (h): o perfil real passa, e 8 sabotagens reprovam:
  - peça sem linha;
  - item de documento sem linha;
  - marca inválida;
  - linha citada sem artigo;
  - linha de peça inexistente;
  - `|` sem escape no trecho;
  - mapa fora de UTF-8;
  - mapa ausente.

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (a19805fe11d95dc0e) | PASS-COM-RESSALVAS | todas as citações do mapa conferidas no texto oficial, sem divergência; MÉDIA: contagem "14 peças" sem reconciliação; BAIXA: mapa fora de UTF-8 estourava exceção; BAIXA: parser sem escape de `\|` | exceção vira achado; split com escape e checagem de 5 colunas; 2 sabotagens novas |
| 2 | Sonnet isolado (a96c428ebd8655796) | PASS-COM-RESSALVAS | as correções de código resistiram a 6 mutações; MÉDIA: a contagem trocada por outra continuava em prosa sem mecanismo; BAIXA: Prova do ADR com 6 sabotagens no índice | número removido, temas numerados; Prova corrigida |
| 3 | Sonnet isolado (a59465b15043a1852) | PASS | nenhum | — |
