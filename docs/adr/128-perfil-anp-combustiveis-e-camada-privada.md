# ADR-128 — Perfil anp-combustiveis e camada privada da empresa

- **Status:** Aceito
- **Data:** 2026-09-28
- **Decisores:** dono (Fabricio), 28/09/2026:
  - D1: pesquisa focada nos trabalhos de distribuição de combustíveis já desenvolvidos;
  - D2: nome `anp-combustiveis`;
  - D3: o perfil traz só o que a norma exige; procedimentos e normas internos ficam na camada privada do usuário, que não acompanha o perfil geral;
  - D4 "a": a camada privada fica na biblioteca privada da empresa;
  - D5 (PENDENTE): o perfil ANP vai ou não às distribuições públicas (ver "Limites").

  Autoria: Opus 5.5.
- **Relação:**
  - segundo perfil do kit regulado (ADR-119), depois do farma-anvisa (ADR-126);
  - a biblioteca da empresa é a do ADR-120;
  - fecha o trabalho `perfil-anp`.

## Contexto
O próximo perfil de aplicação, depois do de medicamentos, é o da ANP. A pesquisa foi feita em duas frentes:
- leitura local, só de leitura, dos projetos de distribuição;
- leitura das normas no texto oficial: DOU, planalto.gov.br, gov.br/anp, gov.br/inmetro, CONFAZ, portal da NF-e e anttlegis.

**A ANP não tem norma que exija do distribuidor validação de sistema computadorizado, integridade de dados ou trilha de auditoria.** A busca foi negativa também nos manuais do i-SIMP.

As exigências reais estão espalhadas em cinco frentes: envio de dados (i-SIMP e estoque diário), guarda de registros por 6 meses, correção a 20 °C, qualidade (boletim, lacre, amostra-testemunha) e instrumentos de medição (INMETRO).

Os procedimentos internos de cada empresa, como tolerâncias de variação e instruções de medição, são conhecimento dela. Pela regra de isolamento, não podem entrar no repositório do framework.

## Decisão
1. **`exemplos/dominio-regulado/compliance-profile-anp-combustiveis.json`.** A categoria é o **papel do sistema**: `movimentacao`, `reporte`, `qualidade` ou `completo`. A norma não tem categoria de software. O perfil traz:
   - normas revogadas, como CNP 6/1970 → ANP 894/2022 e ANP 50/2013 → 968/2024;
   - testes obrigatórios: integridade e retenção de registros;
   - retenção de 6 meses;
   - só o checklist de prontidão como documento.
2. **Mapa `exemplos/dominio-regulado/anp-combustiveis-mapa-normas.md`:** 27 peças, cada uma com artigo, trecho literal e marca, conferidas por `regulado.py mapa`. Fontes e vigência estão em `docs/specs/perfil-anp/fontes.md`.
3. **Camada privada:**
   - `**Empresa:** <e>` na Parte A faz `regulado.py` somar ao perfil público o arquivo `perfis/compliance-profile-<perfil>.json` da biblioteca da empresa, resolvida por `conhecimento.dir_empresa`, interna ou externa.
   - A camada só **acrescenta**: chave nova entra, os dicionários se juntam por chave e as listas se unem sem repetir. Valor nulo, troca de tipo ou valor simples diferente do perfil público reprova, e o público fica. Metadados (`_doc` e chaves com `_`, `note`, `orgao`, `wires_to`, `profile`) não entram na soma. A camada não pode enfraquecer a exigência da norma (QA rodada 5: `null` apagava os testes obrigatórios).
   - Empresa declarada com a biblioteca ausente na máquina reprova e recusa o kit, porque liberar sem os procedimentos internos seria falso PASS.
   - Camada de outro perfil reprova.
   - Sem `**Empresa:**`, nada é lido.
4. **O canário barra a importação do kit farma no perfil ANP.** Sem ERU, sem matriz, sem relatório de validação, e a trilha de auditoria não é exigida.
5. **`knowledge_catalog.py` escreve em UTF-8 no console** (defeito achado nesta pesquisa: o console em cp1252 quebrava no "→").
6. **Leitura de campo `**Nome:**` com valor vazio.** Em `regulado.py` (`_campo`) e em `plano.py` (datas da Parte B), o `\s` atravessava a quebra de linha e o campo vazio devolvia a linha seguinte. As duas leituras passam a usar `[ \t]`, e o placeholder do modelo em `**Empresa:**` conta como não declarado.

## Régua §0
Critério (c): a base normativa das peças é conferida pelo canário, e a camada privada passa de regra em prosa ("fica no meu") a mecanismo. Estende a capacidade `kit-regulado`, sem registro novo.

## Limites
- **Um papel por projeto.** Sistema com vários papéis declara `completo`.
- **Pendências de fonte** (`docs/specs/perfil-anp/fontes.md`, seção 5):
  - texto consolidado oficial da ANP (atosoficiais.com.br respondeu 403);
  - Ato COTEPE vigente com o FCV;
  - Portarias INMETRO 291/2021 e 103/2022 marcadas INFERIDO (ementa, artigo não lido);
  - Res. ANP 807/2020, 884/2022 e 898/2022 marcadas INFERIDO: texto oficial lido de cópia sem URL de origem registrada; reconferir no in.gov.br.
- **Distribuição pública (decisão do dono pendente, D5):** o anonimizador do export troca "combustível(is)" por "do setor regulado" (`tools/anonymize-map.txt`), e as citações literais do mapa ANP deixam de ser literais no pacote público, sem nenhum teste avisar. Opções: (a) excluir os arquivos do perfil ANP do export, que é o recomendado porque o termo está na denylist como dica de setor de cliente; (b) isentar `exemplos/dominio-regulado/` do anonimizador. Até a decisão, não publicar release com este perfil.
- **Chave de metadado na camada é descartada sem aviso:** exigência escrita por engano sob `_x` ou `note` não vale, e a empresa não é avisada. Não enfraquece o perfil público.
- **Verificador sem cobrança do trecho literal:** a coluna do trecho não é conferida (JSON ilegível, BOM na camada e `**Empresa:** nenhuma` também sem teste próprio; mutações sobreviventes da rodada 5).
- **A camada privada da empresa de distribuição foi gravada em 29/09/2026 na biblioteca privada dela**, fora deste repositório (decisão do dono D3: "criar"). Prova ponta a ponta: com `**Empresa:**` da empresa, o kit ganha a peça interna e a saída mostra o caminho da camada; sem a empresa, a peça não aparece.
- **O verificador confere a forma do mapa, não o conteúdo do artigo** (mesmo limite do ADR-126).

## Prova
- `tools/test_regulado.py`:
  - (g): o perfil ANP não tem peça de validação e não exige trilha de auditoria;
  - (h): toda peça do perfil ANP tem artigo no mapa;
  - (i): camada privada:
    - soma o teste obrigatório;
    - soma a peça ao kit sem repetir;
    - sem `**Empresa:**`, não lê;
    - empresa sem camada fica só com o perfil público;
    - biblioteca ausente reprova e recusa o kit;
    - camada de outro perfil reprova;
    - empresa fora do formato reprova, em vez de sumir;
    - camada que não é objeto JSON vira achado;
    - a soma não altera o perfil público (teste direto de `_somar`, com estrutura aninhada);
    - a camada não enfraquece o público: nulo, troca de tipo e valor simples diferente viram conflito; camada com testes obrigatórios nulos reprova; `profile` não textual reprova sem traceback.
- `tools/test_knowledge_catalog.py`, classe `TestConsoleSemUtf8`: recall em console cp1252 sem erro. Sem a correção, o teste fica vermelho (mutação conferida).

## Estado do QA
| Rodada | Revisor | Veredito | Achados | Destino |
|---|---|---|---|---|
| 1 | Sonnet isolado (ab32eb99671a15d9c) | PASS-COM-RESSALVAS | ~15 trechos literais conferidos, todos corretos; 9 regex sem falso positivo em 26 citações vigentes. ALTA: `**Empresa:**` com espaço ou acento sumia em silêncio (falso PASS). MÉDIA: camada que não é objeto JSON quebrava com exceção. MÉDIA: teste "perfil público não alterado" não testava nada. BAIXA: SC Cosit 223 sem cópia local. 4 de 5 mutações mortas. | empresa inválida vira achado; tipo da camada conferido; `_somar` testado direto; SC Cosit marcada INFERIDO |
| 2 | Sonnet isolado (ac09324a8fc4126bb) | FAIL | ALTA (regressão da rodada 1): o placeholder do modelo em `**Empresa:**` reprovava qualquer projeto. MÉDIA: `_campo` com valor vazio lia a linha do campo seguinte. As 3 correções da rodada 1 morreram nas mutações. | placeholder = não declarada; `_campo` e as datas do `plano.py` com `[ \t]` (causa); 4 testes novos; mutação do `plano.py` conferida |
| 3 | Sonnet isolado (a3905fef23a83ad12) | FAIL | ALTA, mesma classe das rodadas 1 e 2 (limite de rodadas de QA): valor real com `<`, `>` ou `\|` era tratado como placeholder e sumia calado. `_campo` sem regressão. 3 de 3 mutações mortas. | **redesenho** da leitura de `**Empresa:**`: em vez de proibir caracteres, lista do que é aceito (vazio, placeholder na forma `<...>` ou `<...> \| nenhuma`, `nenhuma`, nome da biblioteca); o resto reprova; 4 casos novos |
| 4 | Sonnet isolado (aae18c0502056fd9a) | FAIL | ALTA (mesma classe; limite de rodadas atingido): `_valor` cortava no hífen com espaços, e "acme - filial" virava "acme" em silêncio. MÉDIA: a saída não mostrava qual camada entrou. BAIXA: "nenhuma." dá mensagem confusa. | dono autorizou mais uma rodada (29/09, "a"): Empresa lida inteira, com o travessão como único separador de comentário; a saída mostra `camada privada: <caminho> (empresa <e>)`; 3 testes novos |
| 5 | Sonnet isolado (a0ed96f5b671b6d6c) | PASS-COM-RESSALVAS | Isolamento sem achado; 3 citações por amostragem batem com `fontes.md`; 20 de 25 mutações mortas. ALTA: a camada enfraquecia o perfil público (`null` apagava testes obrigatórios e normas revogadas; valor simples trocava exigência). MÉDIA: export anonimiza "combustível" e corrompe citação literal. MÉDIA: peças CONFIRMADO lidas de cópia sem URL e "artigo não lido". BAIXA: `fontes.md` desatualizado; `profile` não textual com traceback; caminho absoluto no mapa. | camada só acrescenta (conflito reprova) com 7 testes novos; `profile` com `str()`; 5 peças e 6 linhas de fontes rebaixadas a INFERIDO; `fontes.md` atualizado; export vira decisão D5 do dono; caminho absoluto mantido (mesmo padrão do farma, ADR-126) |
| 6 | Sonnet isolado (a0ed96f5b671b6d6c, retomado) | PASS-COM-RESSALVAS | ALTA da rodada 5 confirmada fechada (7 cenários reprovam; o caso legítimo passa). MÉDIA: `_doc`/`note` da camada viravam conflito falso. MÉDIA: `profile` em maiúsculas virava conflito falso. BAIXA: S10 sobrevivia. BAIXA: D5 fora do cabeçalho. 12 de 13 mutações mortas. | metadados fora da soma; teste de `carregar` após conflito; D5 no cabeçalho |
| 7 | Sonnet isolado (a0ed96f5b671b6d6c, retomado) | PASS-COM-RESSALVAS | Filtro não permite enfraquecer (4 tentativas sem efeito). BAIXA: chave descartada sem aviso. BAIXA: F3/F5/F6/F7 sobreviviam. 5 de 9 mutações mortas. | teste direto dos metadados (mata F3, F5 e F6; `wires_to` é lista e só une); limite declarado |
