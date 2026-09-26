# Execution report — OPEX de TI: entrega validada e medição da expansão

**Sessão de 23 e 24/09/2026** · repositório de domínio `budget-opex` (privado)
· nenhuma escrita no núcleo do framework

---

## O que foi entregue

- **O desembolso de TI de 2026, apurado do SAP e verificado**: 311 lançamentos,
  R$ 2.682.350,66, conferido por reconstrução independente que diz `PODE ENVIAR`.
- **Dois arquivos**, um para ler e auditar (três abas, com a explicação na frente) e
  outro no layout de importação (aba única). Uma verificação compara os dois célula a
  célula a cada execução.
- **Conjunto documental completo**: relatório técnico, apresentação executiva, nove
  provas, runbook e ponto de retomada.
- **A apresentação em `.pptx` passou a ser gerada do `.md`**, com conferência que exige
  que todo título, bullet e valor em reais cheguem ao slide.
- **A medição que decide a expansão**: a hierarquia de áreas existe no SAP e cobre 100%
  dos 126 centros de custo.

## Números medidos em 24/09/2026

| | |
|---|---:|
| Desembolso, escopo da TI | R$ 2.682.350,66 |
| Despesa reconhecida | R$ 2.894.120,40 |
| Diferença, que é o em aberto | R$ 211.769,74 |
| Universo da empresa, 2026 | 240.652 lançamentos · 126 centros de custo |
| Concentração | 13 centros de custo fazem 80% do valor |

---

## Os defeitos desta sessão, e o que cada um ensinou

A lista existe porque defeito sem registro volta. Sete dos nove já tinham irmão nesta
base.

### 1. Gate tautológico, terceira ocorrência

Um gate comparava a linha contra o **mesmo índice** de onde a linha saiu. Zerar o índice
fazia R$ 2.674.215,42 virar "gasto não previsto" com catorze gates verdes, porque zero
igual a zero é verde.

**Remédio:** eixo alheio. Dois dos gates novos comparam contra **número congelado no
código**, não contra a fonte. Congelar tem custo deliberado: quando o budget mudar de
verdade, o pipeline fica vermelho e alguém precisa olhar.

### 2. Gate vazio, quarta ocorrência

O gate 5h nasceu julgando **zero casos** e mostrando verde. A condição que ele exigia
nunca acontecia nos dados reais.

**Remédio:** todo gate novo imprime **quantos casos julgou**. Verde com zero julgados
passou a ser visível na própria saída.

### 3. Guarda atrás de cano, terceira ocorrência

`confere_entrega.py | tail -3` devolveu o código do `tail`. O `NÃO ENVIAR` passou
despercebido **dentro do comando que verificava o entregável**.

**Remédio:** a guarda roda sozinha e o código se lê depois. Está escrito no README e no
ponto de retomada.

### 4. Heredoc engolindo barra invertida, sétima ocorrência

Voltou duas vezes nesta sessão. O remédio já era conhecido — payload com escape vai pelo
Write — e eu não o apliquei na primeira.

### 5. Caminho cravado, três rodadas

O dono reorganizou as pastas e o gerador parou. Consertei seis arquivos, sobraram três,
as guardas pegaram. No dia seguinte a pasta mudou de novo e o resolvedor **seguiu
sozinho**.

**Aprendizado que vale além deste projeto:** caminho cravado se multiplica porque cada
arquivo novo copia o do lado. Só para de doer quando não resta nenhum.

### 6. Limpeza por contagem de menção, não por importação

Arquivei dois módulos que estavam **em uso**, decidindo por quantos arquivos citavam o
nome. O que decide é a linha de import. Quatro guardas ficaram vermelhas em segundos.

### 7. Prosa que envelhece sem aviso

Três trechos da apresentação executiva viraram mentira **pela medição da própria sessão**.
Nenhum gate lê narrativa.

**Remédio parcial:** todo número da apresentação é calculado na geração, nunca digitado.
Sobra o texto, que continua sendo o ponto cego.

### 8. Teste escrevendo no artefato real

Um QA adversarial rodou o pipeline **com sabotagens** por cima do arquivo que ia à
diretoria. E eu repeti a classe ao criar um terceiro arquivo de saída sem redirecioná-lo
nos testes.

**Remédio:** todo teste grava em pasta temporária, e isso está escrito no README.

### 9. Erro de leitura na saída do meu próprio teste

O caso limpo saía rotulado `PEGO`, que faz quem lê entender o oposto. Saída de teste
existe para ser lida.

---

## O que o QA adversarial pegou, em dois ciclos

**Ciclo 1 — o gerador.** REPROVAR. Três fronteiras atravessadas sem acionar nada:
identidade do contrato, índice de orçamento e status por mês. Os três ataques viraram
teste permanente e hoje ficam vermelhos.

**Ciclo 2 — as sondagens SQL.** REPROVAR. Eu havia usado nove campos de três tabelas sem
sondar as colunas, repetindo a anatomia de um erro que já custara duas consultas mortas.

**E o QA errou uma vez.** Afirmou que uma tabela não tinha evidência de execução; tinha,
registrada no runbook. Conferir o relatório do agente antes de aceitar não é formalidade.

**O achado mais valioso veio da correção, não do achado.** O QA apontou que um filtro de
contas validado numa área podia não generalizar. A correção não foi removê-lo: foi
transformá-lo em **coluna ao lado do total**. Medido depois: ele captura 56% do valor da
empresa, e centros de custo inteiros ficam com zero. Se eu tivesse apenas removido, o
número sairia certo e ninguém saberia o tamanho do que ficava de fora.

---

## Padrões que valem para o framework

1. **Aproximação de uma direção só é decisão válida.** A consulta de cobertura compara só
   igualdade, então só pode superestimar quem está fora. Zero nela encerrou a questão.
   Declarar a direção do erro transforma medida imperfeita em resposta definitiva.
2. **Filtro validado numa amostra vira coluna, não cláusula.**
3. **Critério de aceite escrito antes de rodar.** Toda sondagem declara o que significaria
   cada resposta possível. Critério definido depois de ver o número transforma qualquer
   número em confirmação.
4. **Congelar valor no código é atrito deliberado.** A alternativa — reler a fonte e
   aceitar o que vier — é o que deixa a fonte zerada passar despercebida.
5. **Gate que reclama de mudança legítima é gate funcionando.** A conferência barrou o
   entregável porque o contrato mudou; o erro seria afrouxá-la.

---

## Estado ao fechar

- `budget-opex`: `main` sincronizada, árvore limpa, sete guardas verdes.
- `metacognition-framework`: nenhuma escrita no núcleo. Duas sessões-irmãs foram
  respondidas confirmando que este trabalho é de domínio.
- **Pendente com o dono:** enviar o arquivo à diretoria e reenviar a cópia ao SharePoint,
  que subiu vazia.
- **Próximo passo técnico:** medir o preenchimento dos campos de área no cadastro de
  centro de custo.
