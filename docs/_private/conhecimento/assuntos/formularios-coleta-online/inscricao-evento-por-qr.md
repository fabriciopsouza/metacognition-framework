# Inscrição de evento por QR Code: armadilhas medidas
> Saber puro de assunto (sem dado de empresa). Origem: inscrição de evento interno com público externo, 10/2026.
> Cada entrada separa o que foi medido do que foi deduzido.

## conta Google nova com formulário criado por script é bloqueada
- **Tipo:** fato
- **Classe:** configuração
- **Sistema:** Google Forms / Google Drive / Apps Script
- **Fonte:** medição própria. Os 3 links (2 formulários e 1 planilha) responderam HTTP 403 com o texto "Não é possível acessar este item porque ele viola nossos Termos de Serviço", 1 dia depois de a montagem passar em todos os testes.
- **Verificado em:** 16/10/2026
- **Confiança:** CONFIRMADO por medição HTTP dos 3 links
- O que foi medido: a conta era nova (criada no mesmo dia), os formulários foram criados por Apps Script e pediam um número de identificação. No bloqueio, o login passou a exigir uma verificação por celular que não concluía.
- Causa: INFERIDO. O padrão "conta nova + formulário gerado por script + pede identificação" parece golpe para o filtro do Google, que não informa o motivo.
- Regra: para coletar dados de pessoas, usar a conta do tenant corporativo. Nunca conta gratuita recém-criada, nem formulário gerado por script. Recurso ao Google leva dias: não serve para prazo curto.
- O QR já impresso aponta para o link bloqueado. Apague os QR gerados assim que o link cair.

## formulário Microsoft com link aberto e planilha sincronizada
- **Tipo:** fato
- **Classe:** configuração
- **Sistema:** Microsoft Forms + Excel online
- **Fonte:** medição própria, roteiro executado por 2 pessoas (48 passos), com prova de alinhamento após resposta nova
- **Verificado em:** 19/10/2026
- **Confiança:** CONFIRMADO por teste de execução
- Medido: com "Qualquer pessoa pode responder", o formulário abre no celular pelo 4G sem login. Por isso, o público externo responde.
- Medido: "Respostas → Abrir no Excel" cria uma planilha online sincronizada. As colunas criadas logo à direita da tabela passam a fazer parte dela. A resposta nova entra no fim, e as marcações feitas à mão nas linhas antigas ficam na linha certa.
- Regra de uso para quem marca na planilha: não ordenar, não apagar linha ou coluna, não editar as colunas das respostas. Filtrar pode.
- Respostas de teste: marcar "TESTE – IGNORAR" em vez de apagar. Que apagar quebre o sincronismo é INFERIDO, não testado.
- Teste que decide o plano, a fazer antes de montar: um formulário de 1 pergunta com link aberto, respondido no celular sem Wi-Fi.
- Não verificado: se o sincronismo sobrevive à transferência do formulário para outro dono. Ao transferir, fazer 1 resposta de teste.

## montar inscrição de evento por QR em meio dia com 2 executores
- **Tipo:** runbook
- **Pergunta:** Como montar inscrição e votação por QR, com público externo e controle de entrega, sem script e em meio dia?
- **Fonte:** execução medida do roteiro (checklist em Excel com Painel "onde parou" por pessoa), 19/10/2026
- **Verificado em:** 19/10/2026
- **Confiança:** CONFIRMADO por execução (48/48 passos, 0 erros, cerca de 2h40 de relógio)
- Pessoa B começa pelo teste do link aberto (10 min) e avisa. Depois monta a votação. À tarde, cria as colunas de controle e confere os testes de A.
- Pessoa A monta o formulário de inscrição: seções, ramificação "não concordo → fim" e "sem familiar → fim", QR e planilha sincronizada. À tarde, faz as inscrições de teste, inclusive um externo sem identificação.
- O checklist em Excel tem as colunas Quem · Turno · "Espere antes" · Status (lista) · Erro · Resposta do responsável. O Painel calcula onde cada um parou. Ninguém apaga linha: passo que não serviu vira "Substituído".
- Pergunta obrigatória dentro de seção pulada pela ramificação não trava quem pula. O teste "sem familiar" provou isso.
- Público externo: identificar pelo telefone. O campo de identificação interna fica opcional.

## texto de cartaz e formulário sem quebra errada
- **Tipo:** fato
- **Classe:** conceito
- **Fonte:** prática de tipografia: espaço não separável U+00A0. Medido no cartaz gerado.
- **Verificado em:** 21/10/2026
- **Confiança:** INFERIDO
- O QR que o próprio formulário gera leva o título cortado onde couber. Para impressão, gerar o cartaz com as linhas definidas à mão e recusar linha que não cabe.
- Espaço não separável (U+00A0) mantém juntos "3 km", "22/11" e o nome do evento com o ano. Que o Forms respeite U+00A0 no título não foi testado.
- Opção de resposta que ninguém usa (ex.: "Outro" com medidas livres) só cria trabalho manual. Tirar, a menos que a área peça.
