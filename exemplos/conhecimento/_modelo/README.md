# Biblioteca de conhecimento — modelo e método (ADR-120)

Procedimento para construir e consultar, durante o trabalho, o conhecimento que um projeto descobriu e outro não
deve refazer. Este diretório é o **modelo**. A biblioteca de cada empresa é uma cópia dele, mantida pelos projetos
daquela empresa. Verificação: `python tools/conhecimento.py verificar <raiz> --empresa <empresa>`.

## 1. Definições

| Termo | Definição |
|---|---|
| Biblioteca | Pasta com o conhecimento reutilizável de uma empresa, na estrutura da seção 2 |
| Entrada | Um bloco `## <nome>` com campos fixos (seção 4) |
| Termo | Entrada do dicionário: conceito definido uma vez, no seu nível, com relações |
| Retrato | Número, contagem ou resultado medido numa data: histórico, não vence, nunca é citado como valor atual |
| Fonte única | Consulta em uso num projeto fica no projeto; a biblioteca aponta para ela (**Aponta para:**) |

## 2. Estrutura

```
<raiz>/
  conhecimento.json                         prazos de validade e versão atual de cada sistema
  INDICE-PROJETOS.md                        uma linha por projeto
  perfis/<perfil>/DICIONARIO.md             termos do perfil regulado (quando houver)
  assuntos/<assunto>/DICIONARIO.md          termos de saber puro de assunto, compartilhados entre empresas
  assuntos/<assunto>/<tema>.md              consultas, fatos, pesquisas e runbooks de assunto
  empresas/<empresa>/DICIONARIO.md          termos da empresa e a entrada `## Identificadores`
  empresas/<empresa>/conhecimento.json      versões de sistema da empresa (opcional; prevalece sobre o da raiz)
  empresas/<empresa>/<area>/<assunto>.md    consultas, fatos, pesquisas e runbooks
```

1. Nível: perfil regulado → assunto → empresa → projeto. O termo de projeto mora no glossário do projeto, e o índice
   aponta para ele.
2. Dentro da empresa: área de negócio → assunto.
3. O sistema-fonte é campo da entrada, não pasta.
4. **Isolamento entre empresas (regra do dono, 27/09/2026):** o conhecimento de uma empresa (processo, centros,
   códigos, valores, consultas, nomes) nunca aparece no trabalho de outra. Só o saber puro de assunto (sistema no
   padrão, sem customização) vai para `assuntos/`.
   - Busca e verificação leem só `empresas/<empresa>/`, `assuntos/` e `perfis/`. Sem `--empresa`, a empresa sai do
     `INDICE-PROJETOS.md` pelo diretório atual; sem resolução, o comando recusa. `--empresa nenhuma` = só assuntos e
     perfis; `--empresa todas` = manutenção da biblioteca inteira.
   - Empresa aponta para assunto e perfil; assunto e perfil não apontam para empresa; empresa não aponta para outra
     (relação ou caminho de projeto): achado bloqueante.
   - Entrada em `assuntos/` com identificador de empresa reprova: nome da empresa, **Valores:** da entrada
     `## Identificadores` (tipo `identificadores`, só no DICIONARIO.md da empresa), caminho e repositório de projeto do
     índice, objeto Z*/Y*, campo ZZ*/YY*, tipo de movimento 9xx ou X/Y/Z, caminho de usuário.
5. **Biblioteca da empresa fora do framework (emenda 2 do ADR-120):** cada empresa num repositório privado próprio,
   submódulo `empresas/<empresa>` de um repositório-pai. Em cada máquina, só o submódulo da empresa daquela máquina é
   inicializado (nunca `--recursive`).
   - O repositório da empresa tem o marcador `.conhecimento-empresa`, o `DICIONARIO.md`, as áreas, o
     `INDICE-PROJETOS.md` e o `conhecimento.json` dela.
   - A raiz aponta para o pai em `conhecimento.json` → `"bibliotecas": ["<pasta>"]`; pasta ausente é ignorada.
   - `python tools/conhecimento.py publicar <raiz> --empresa <empresa>` grava em `assuntos/_identificadores/` o
     sha256 dos identificadores da empresa. A máquina que não tem a biblioteca dela ainda reprova esses
     identificadores em `assuntos/`, sem ver o texto. O `verificar` acusa a lista desatualizada.
   - O `--recall` omite relatório de sessão que cita outra empresa.

## 3. Método

### 3.1 Consultar (antes de pesquisar, perguntar ou escrever consulta)
1. Buscar: `python tools/knowledge_catalog.py --recall --context "<palavras>" --conhecimento <raiz> --empresa <empresa>`
   (dentro da pasta de um projeto do índice, `--empresa` pode ser omitido).
2. Achou e está válido: reusar e citar o nome da entrada.
3. Achou e está vencido (`python tools/conhecimento.py vencidos <raiz> --empresa <empresa>`): refazer só aquilo e
   atualizar a entrada.
4. Não achou: registrar "nada encontrado" na especificação e seguir.

### 3.2 Construir (no ato, não no fim do projeto)
1. Termo confirmado ou pesquisado vira entrada no DICIONARIO.md do nível certo, no mesmo bloco de trabalho.
2. Consulta rodada com resultado exportado vira entrada de assunto. Se estiver em uso no projeto, a entrada aponta
   para ela. No 2º projeto que a reusa, ela se muda para a biblioteca.
3. Número medido entra como `fato` de classe `retrato`, com a data.
4. Ao fechar o bloco, o docops registra o que ficou reutilizável ou declara "nada a registrar".

### 3.3 Quando refazer
| Classe | Refazer quando |
|---|---|
| estrutura (tabela, campo, objeto) | a versão do sistema em `conhecimento.json` muda |
| configuração | 6 meses (ajustável em `validade_meses`) ou mudança conhecida |
| regra de negócio · conceito | 12 meses ou mudança de processo confirmada pela área |
| retrato | nunca: é histórico; para o valor de hoje, rode a consulta de novo |
| qualquer uma | um resultado novo a contradiz: preencher **Contestado em:** |

## 4. Formato da entrada

```
## <nome>
- **Tipo:** termo | consulta | fato | pesquisa | runbook | identificadores
- **Fonte:** <arquivo e linha, documento ou pessoa, com data>
- **Verificado em:** dd/mm/aaaa
- **Confiança:** CONFIRMADO por <quem> | INFERIDO | REFUTADO
```

| Tipo | Obrigatórios além dos comuns | Opcionais |
|---|---|---|
| termo | **Definição:** | **Relações:** (é um · parte de · regulado por · medido por · sinônimo de: `é um: A; parte de: B`), **Campo:** |
| consulta | **Pergunta:**, **Sistema:**, **Versão:** e um bloco de código com o texto pronto | **Evidência:**, **Aponta para:** |
| fato | **Classe:** (estrutura exige **Sistema:** e **Versão:**) | **Evidência:** |
| pesquisa · runbook | **Pergunta:** | **Classe:**, **Evidência:**, **Aponta para:** |
| identificadores | **Valores:** (separados por `;`), só no DICIONARIO.md da empresa; fica fora da busca | — |

Todos aceitam **Contestado em:**. Caminho em **Evidência:** ou **Aponta para:** tem de existir.

## 5. Nunca entra
- Credencial (senha, token, chave) e documento de identificação de pessoa. O verificador reprova.
- Valor de negócio, resultado e nome de responsável **entram**. Onde a biblioteca mora (repositório privado ou
  outro local) é decisão de quem a mantém.
