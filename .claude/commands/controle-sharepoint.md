---
description: OPÇÃO — laço da List do SharePoint: gera o CSV de ida e lê a volta da gestão (ADR-113)
---

Execute o **laço da List do SharePoint**, seguindo `_shared/controle-projeto/SKILL.md §List`
(fonte única — não duplicar a lógica aqui).

**Isto é OPÇÃO, não padrão.** O padrão do pacote é planejar, executar, lançar ação no portal e
manter cronograma. Projeto que não usa SharePoint declara
`"adotado": {"sharepoint-list": {"usa": false, "por_que": "..."}}` e nunca vê este comando.

## O laço, e o defeito que ele conserta

```
IDA    --exportar            -> LIST-backlog.csv   (derivado, SÓ SAI)
       o dono/automação importa na List
       a gestão preenche responsável, situação, prazo, prioridade
VOLTA  a automação grava        LIST-retorno.csv   (insumo, SÓ ENTRA)
       --receber             -> escreve no estado do projeto
```

**Arquivo que sai nunca é o mesmo que entra.** O desenho ingênuo — a automação escrevendo de volta
no próprio backlog — destrói dado em silêncio, porque o backlog é *gerado*: a próxima regeneração
sobrescreve o que a gestão preencheu, sem erro e sem aviso.

## Passo a passo

1. `python tools/nucleo.py controle_sharepoint --exportar` (ou `--projeto <caminho>` do núcleo).
2. **Diga ao dono o que a saída avisou** — quais colunas passam do limite e precisam ser
   *"Várias linhas de texto"* na importação; e que `responsavel` sai **vazia de propósito**.
3. Volta: `--receber` **primeiro em ensaio**. Só depois `--receber --confirmar`.
4. **Relate as quatro listas que o ensaio produz**, nenhuma delas é ruído:
   - **muda** — o que a List mandou e vale;
   - **IGNORADA** — estrutura do trabalho (título, fase, dependência, o que/onde fazer). Nasce de
     elicitação, não de reunião de status. Se a mudança for legítima, faz-se no repositório;
   - **id que não existe** — tarefa criada direto na List. Ela nasce no repositório, não lá;
   - **RECUSADO na fronteira** — valor de prioridade, prazo ou situação que não deu para
     interpretar, e por isso **não entrou no estado**. É a lista mais fácil de engolir e a que
     mais custa caro: o dono precisa saber que aquele prazo que ele digitou na reunião foi
     descartado por formato, senão ele sai achando que mudou. *A redação anterior dizia "três
     listas" e omitia esta — achado do QA adversarial; o código sempre produziu as quatro
     (`tools/controle_sharepoint.py:349`).*
5. **Se houve mudança de prazo, leia as CONSEQUÊNCIAS em voz alta.** Prazo movido numa planilha não
   avisa que a dependência ficou depois nem que passou do limite externo. Isso não impede a
   mudança — replanejar é direito da reunião — mas não pode passar calado.
6. Depois de `--confirmar`, rode a cadeia determinística do projeto para propagar.

## Duas recusas reais do importador, e o que elas ensinaram

| erro na tela | causa medida | o que ficou no código |
|---|---|---|
| `Esquema inválido fornecido` | quebra de linha dentro de célula, separador `;`, BOM | vírgula, UTF-8 sem BOM, `QUOTE_ALL`, quebra achatada, autoconferência de linhas físicas |
| `Linhas 6 e 50 foram omitidos` | **nome** que o catálogo não resolveu — as duas linhas de uma mesma pessoa | `responsavel_no_import: false` — o nome entra pela tela ou por automação pós-criação |

A segunda custou uma correção **errada** antes da certa: culpou-se o tamanho dos campos e o
arquivo foi enxugado, jogando fora três colunas úteis — com a evidência contrária já na tela (18
linhas passavam de 255 caracteres e importaram bem). Contar as linhas a partir do primeiro **dado**,
e não do cabeçalho, era o que faltava.
