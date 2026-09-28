> Parte de `_shared/project-docs/SKILL.md` (entrada enxuta desde 28/09/2026, B3c). Conteúdo copiado integral da versão anterior; a entrada aponta para cá.

## §3.2 — RUNBOOK: o documento de quem vai EXECUTAR com as próprias mãos

Quando o resultado depende de alguém **operar** — tela de sistema, terminal, console de
administração, configuração de credencial — o entregável **não é a explicação**. É o runbook.

**Por que é propriedade do conjunto, e não estilo:** explicação vive em conversa, e conversa não
sobrevive a queda de conexão, compactação de contexto, troca de sessão nem troca de pessoa. O
começo é a primeira coisa que se perde, porque é a parte que o autor acha óbvia e o executor não
tem. *(Caso: operador perdeu a conexão no meio de uma configuração e não sabia voltar à tela; o
"como chegar" estava numa mensagem rolada para cima.)*

### As 5 marcas de um runbook (as 5 valem, ou é explicação com passos numerados)

| # | Marca | O que evita |
|---|---|---|
| **R1** | **Passo 0 = como chegar**: endereço direto **e** caminho de menu **e** o sinal de que chegou ("você chegou quando vê X") | o executor sabe o que fazer e não sabe **onde** |
| **R2** | **Cada passo declara o resultado esperado** | não dá para saber se funcionou, nem onde retomar |
| **R3** | **Autossuficiente**: nenhum passo depende do que foi dito em conversa | o runbook morre junto com a sessão |
| **R4** | **Reversão explícita**, dizendo **o que não apagar** enquanto o novo não funciona | operador destrói o caminho de volta |
| **R5** | **O que a documentação oficial NÃO cobre**, visto em tela e datado | a mesma descoberta é paga de novo no próximo projeto |

**Teste binário (R3):** *se a conexão cair agora, o arquivo sozinho faz retomar?* Não → não é runbook.

**Régua §0:** runbook que já existe se **reescreve**; não se acrescenta outro ao lado.

### §3.2.1 — Credencial de serviço: o que todo runbook desse tipo tem de dizer

Criar credencial para máquina falar com sistema corporativo repete os mesmos tropeços em qualquer
produto. O runbook declara os seis:

> **Marca de confiança destes seis: `INFERIDO`.** Vêm de **um** caso real de configuração de
> credencial de serviço, generalizados por decomposição — **nenhum outro produto os confirmou
> ainda**. Trate como ponto de partida a ajustar, não como norma medida. *(As marcas R1–R5 acima
> têm origem diferente: nasceram do caso citado no §3.2, de operador que perdeu a conexão.)*

1. **Qual identidade a credencial carrega** — e que ela herda as permissões de quem a gerou.
2. **O menor conjunto de permissões que resolve**, com a **linha que separa leitura de escrita**
   escrita por extenso. Permissão de leitura se acrescenta depois; **escrita concedida por descuido
   não se desfaz**.
3. **⚠️ O modo de autenticação** — e que **escolher o errado só falha lá na frente**, não no ato.
   Se o console oferecer mais de um, o runbook diz **qual** e **por quê**.
4. **O que é secreto e o que não é.** Identificador de cliente normalmente é público por desenho;
   o segredo vai para o cofre do sistema operacional e **nunca** para arquivo, chat ou terminal.
5. **O que só aparece uma vez** na tela de criação — e em que momento copiar.
6. **Se dá para editar depois.** Campo somente-leitura na edição significa: **errou, apaga e refaz**.
   Descobrir isso depois custa uma credencial inteira.

> **A ordem importa:** verificar o modo de autenticação **antes** de gravar o segredo no cofre. Ao
> contrário, perde-se a credencial que funcionava para ganhar uma que talvez não sirva.

---
