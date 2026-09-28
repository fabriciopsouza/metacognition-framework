> Parte de `_shared/project-docs/SKILL.md` (entrada enxuta desde 28/09/2026, B3c). Conteúdo copiado integral da versão anterior; a entrada aponta para cá.

## §1 — O teste binário, antes de tudo

Um conjunto documental está pronto quando:

> **Uma pessoa nova — ou outra sessão de IA — retoma o projeto sem precisar perguntar nada a
> ninguém.**

Não é métrica de estilo. É verificável: entregue a documentação a quem não participou e peça que
diga qual é o próximo passo. Se a pessoa perguntar, o documento falhou — e a correção é do
documento, não da pessoa.

Corolário que muda o que se escreve: **o leitor-alvo não é quem já sabe.** Todo documento é escrito
para quem chega depois, inclusive você daqui a três meses.

---

## §2 — As 7 propriedades obrigatórias

Estas são o padrão. O conjunto de arquivos (§3) é consequência delas, não o contrário.

### 2.1 Dono único por fato
Cada afirmação tem **um** arquivo dono. Os demais **apontam**, nunca copiam.
Um mapa de fontes declara quem é dono do quê e o que vive fora do repositório.

*Por que:* duas cópias divergem, e a divergência é descoberta pelo leitor, não pelo autor.
*Modo de falha real:* uma métrica-chave da base aparecia por extenso em cinco arquivos — e o próprio
mapa de fontes afirmava que os demais "apontavam". Não apontavam.

### 2.2 Marca de confiança em toda afirmação relevante
`CONFIRMADO` (medido ou em fonte oficial, com prova apontada) · `INFERIDO` (deduzido, dizendo de
onde) · `DESCONHECIDO` (**resposta válida; inventar não é**) · `REFUTADO` (acreditávamos, medimos,
estava errado).

**Crença refutada nunca é apagada.** Fica registrada com a prova.
*Por que:* crença apagada volta sozinha. Num caso observado, voltou **seis semanas** depois de
derrubada, e voltou pela boca de quem tinha participado da refutação.

### 2.3 Prova com consulta reproduzível
Um arquivo por verificação, contendo: pergunta em uma frase · **a consulta exatamente como
executada** · resultado · conclusão em uma frase, com a marca.

*Por que a consulta é obrigatória:* sem ela ninguém reproduz, ninguém confere se ainda vale, e
ninguém descobre que a conclusão dependia de um recorte que mudou. **O número envelhece; a consulta
continua respondendo.**

### 2.4 Número sempre com data
Número sem data é retrato sem legenda: não dá para saber se ainda vale. Todo número no repositório
é retrato com data — a fonte é a consulta.

### 2.5 Ponto de retomada explícito
Um documento único responde, nessa ordem: onde estamos · o que foi feito nesta sessão · **o próximo
passo, em ordem** · o que está travado e **por quem** · o que você precisa saber para não errar ·
decisões em aberto e **quem decide cada uma** · como conferir que tudo isto é verdade.

*Detalhe que separa útil de decorativo:* bloqueio sem **nome de quem destrava** não é bloqueio, é
lamento. Decisão em aberto sem **nome de quem decide** não é decisão, é desejo.

### 2.6 Vocabulário e jargão
Termo técnico ou código interno aparece **com a explicação junto, na primeira vez**. Nunca
"aplicamos o INV-9" — escreva o que a verificação faz.

Em domínio sensível ou regulado, o produto **sinaliza, não julga**: "fora do padrão, a verificar",
nunca veredito de irregularidade. Isso não é estilo — é o que torna o resultado defensável.

### 2.7 Fronteira declarada entre as partes
Se o repositório tem uma parte reutilizável e outra específica de domínio, a fronteira é escrita e
**verificada por comando** (§4). Sem isso, a parte reutilizável é contaminada em silêncio e perde a
razão de existir.

---
