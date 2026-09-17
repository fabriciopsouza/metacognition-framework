# Execution-report — cross-IA · tier OWNER (privado, não distribuído)

**Bloco:** diagnóstico de logon SAP GUI em `copiloto-automacoes-sap` (23–24/08/2026)
**Origem:** Claude Code / Opus 5 · projeto-cliente com automação SAP
**Motivo deste report:** pedido explícito do dono — *"Coloque uma GARANTIA no
framework que isso jamais ocorra"*. **Não implementado aqui de propósito**: entra
como insumo para o framework decidir e mecanizar.

- **Tempo (wall-clock):** ~2 dias de sessão (23 e 24/08/2026)
- **Custo real do desvio:** 2 hipóteses refutadas, código escrito para as duas,
  2 tentativas de logon gastas na conta pessoal do dono em produção
- **Tempo que a orientação dele levou para resolver:** ~40 segundos (uma execução)
- **Testes:** 631 passando **durante todo o desvio** — ver §2
- **Tokens / turnos / arquivos:** NÃO MEDIDO

---

## 1. O modo de falha, nomeado

**`hipótese-própria-preferida-à-referência-apontada`.**

O humano aponta um artefato que **afirma funcionar** — um repositório, um caminho,
uma execução anterior — e o agente, em vez de **executá-lo ou lê-lo**, constrói e
testa hipóteses próprias sobre a causa.

Falas reais do dono, em ordem, na mesma sessão:

1. *"REITERO que o logon funciona NORMALMENTE nos projetos abaixo e que vc não
   deve estar realmente reutilizando o que já funciona. NÃO tente reinventar a
   bola. Os módulos que propus foi exatamente para evitar isso: um domingo
   inteiro perdido"*
2. *"vamos fazer o seguinte? Rode a usmm_old."*
3. *"CARA NÃO REINVENTA A RODA: RODE o usmm_old"*
4. *"veja a versão que FUNCIONOU, afirmo, e use o mesmo mecanismo"*

Só na quarta o agente executou. A execução respondeu em 40 s: as seis escritas de
tela pegaram e o SAP devolveu *"O nome ou a senha não está correto"* — e resposta
de credencial só existe se os campos chegaram preenchidos. Ou seja **o mecanismo
nunca teve defeito**; a senha estava errada. As duas hipóteses do agente (tela
redesenhada por dependência de mandante; referência COM obsoleta na subida do
programa) morreram na primeira medição que as testou de verdade.

## 2. O que torna isto grave, e não apenas ineficiente

**A suíte de testes defendeu ativamente a crença errada.** O agente escreveu dois
testes que fixavam a própria hipótese — um exigindo escrita condicional de
mandante, outro exigindo o laço de três tentativas. Com eles, 631 testes passavam
enquanto o código encodava uma hipótese falsa, e **remover o código errado quebrava
a suíte**. O verde deixou de ser evidência e passou a ser inércia.

Nenhum gate existente pega isso: todos avaliam o código contra o que o autor
declarou querer. Nenhum pergunta *se a premissa foi medida*.

Segundo agravante: **o experimento diagnóstico não podia falhar.** O agente
escreveu um modo `--testar-logon-automatico` para testar "a automação sobe o SAP
Logon e a escrita se perde" — mas ele exigia o objeto COM `SAPGUI` **já existente**,
isto é, exigia o programa já aberto. Nunca exercitou a única variável em disputa, e
por isso **passou**. Um experimento que não alcança a condição que investiga não é
experimento: é confirmação com aparência de método.

## 3. Placar gate × achado

| Achado | Quem pegou | Gate que deveria ter pego |
|---|---|---|
| Hipótese do mandante (falsa) — código escrito para ela | o **humano**, mandando ler o projeto de referência | `referencia-apontada` (não existe) |
| Hipótese da referência COM obsoleta (falsa) — código + função nova | o **humano**, na 4ª insistência | `referencia-apontada` (não existe) |
| 2 testes fixando hipótese não medida | o próprio agente, só **depois** de medir | `hypothesis-ledger` (não existe) |
| Experimento incapaz de alcançar a condição investigada | o próprio agente, ao consertá-lo | `experimento-com-controle-negativo` (não existe) |
| 2 tentativas de logon gastas em conta de produção | o humano leu o log | — (dano já feito) |

## 4. A garantia proposta — quatro mecanismos

Deliberadamente mecanismos, não conselhos: conselho sobre humildade epistêmica é
exatamente o tipo de instrução que um agente lê, concorda e não obedece.

### 4.1 Gate `referencia-apontada` (fail-closed)

**Disparo:** a mensagem do humano contém ponteiro para artefato existente que ele
afirma funcionar — caminho de arquivo/repo, ou padrão lexical (*funciona em*,
*já fizemos*, *não reinvente*, *use o mesmo*, *veja o projeto*, *a versão que
funcionou*).

**Efeito:** enquanto o ponteiro não for **consumido**, o agente fica proibido de
commitar mudança guiada por hipótese no mesmo subsistema. Consumir = registrar

```yaml
referencia_consultada:
  ponteiro: "<o que o humano apontou>"
  como: executei | li
  evidencia: "<saída real da execução, ou linhas citadas do arquivo>"
  veredicto: confirmou | derrubou   # a hipótese do agente
```

**Por que fail-closed:** a falha aqui é sempre a mesma — o agente *pretende* olhar
a referência "depois de testar uma coisa rápida". Não existe "depois".

### 4.2 `hypothesis-ledger` — nenhum teste fixa hipótese não medida

Toda hipótese entra num registro **antes** de virar código, com o campo obrigatório
*"qual medição a derrubaria"*. E a regra que faltava:

> **Teste que fixa comportamento derivado de hipótese só é aceito se citar a
> medição que a confirmou.** Sem medição, o teste nasce marcado `hipotese:`, não
> conta como cobertura, e o gate avisa que a suíte contém crença, não evidência.

É isto que impede o verde de virar inércia. No caso real os dois testes teriam
nascido marcados, e removê-los seria rotina em vez de "quebrar a suíte".

### 4.3 `experimento-com-controle-negativo`

Ferramenta diagnóstica escrita para testar a condição X precisa declarar **como
alcança X**, e precisa ser capaz de **falhar**. Se o experimento não consegue
sequer produzir X, ele é inválido — e não "passou".

Regra curta: *um experimento que não pode falhar não mede nada.*

### 4.4 `medicao-mais-barata-primeiro`

Antes de implementar correção de causa desconhecida, declarar:

- qual é a **medição decisiva mais barata** disponível;
- se ela não foi feita, **por quê**.

No caso real a medição mais barata era executar o projeto que o dono apontou: 40
segundos. As hipóteses custaram dois dias. A assimetria não foi percebida porque
ninguém foi obrigado a escrevê-la lado a lado.

## 5. Detecção: framework × humano

**Humano: 4. Framework: 0.**

Os quatro achados de causa vieram do humano insistindo, não de gate. E o humano
teve de subir o tom (*"CARA NÃO REINVENTA A RODA"*) para ser obedecido — sinal de
que o custo da correção estava recaindo inteiro sobre ele. Um framework em que a
única defesa contra a teimosia do agente é a repetição do humano transfere ao
humano justamente o trabalho que o framework existe para fazer.

## 6. Boas práticas — o que funcionou e é reutilizável

- **Rodar os dois lados no mesmo minuto, na mesma máquina.** O A/B (referência →
  sessão em 2 s; projeto novo → nenhuma sessão em 60 s) separou "código" de "alvo"
  de uma vez. Comparação simultânea vale mais que log histórico.
- **Desconfiar da própria medição anterior.** Uma checagem de porta caía para
  `ping` quando o cmdlet falhava e devolvia `True` sem valor. Refeita com
  `TcpClient`. Medição com fallback silencioso é pior que medição ausente.
- **Guarda que protege recurso, não mecanismo.** A única coisa preservada da
  invenção foi *recusar apertar Enter com a tela incompleta* — não altera a
  sequência de referência e evita gastar tentativa de conta. Distinguir "mudança de
  mecanismo" de "guarda de recurso" é a régua que permitiu descartar o resto sem
  medo.
- **Experimento que se autolimpa.** O modo diagnóstico passou a fechar o programa
  que ele mesmo subiu: experimento que altera a própria variável ao rodar não é
  repetível.

## 7. Lições por skill (agnóstico de domínio)

- **dev:** referência apontada pelo humano é **entrada de dados**, não sugestão de
  leitura. Executá-la vem antes de hipótese própria — e "reutilizar" significa
  copiar a sequência que funciona, não uma variação dela.
- **qa-critic:** teste escrito pelo autor da hipótese pode blindar a hipótese.
  Exigir procedência de medição em teste que fixa comportamento diagnóstico. E
  verificar se o experimento **alcança** a condição que alega testar.
- **architect:** código que existe para hipótese refutada é pior que código a
  mais — ensina o defeito errado a quem ler depois. Refutação deve disparar
  remoção, não só correção.
- **discovery:** ordenar investigação por **custo da medição decisiva**, não por
  elegância da hipótese. Escrever os dois custos lado a lado antes de escolher.
- **docops:** registrar hipótese **derrubada** com a medição que a derrubou. Duas
  hipóteses caíram neste bloco; sem o registro, a terceira sessão reinventa a
  primeira.
