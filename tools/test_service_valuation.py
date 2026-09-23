#!/usr/bin/env python3
"""Canario da skill service-valuation (ADR-114) — exit 0 = as travas existem e os numeros fecham.

O criterio de aceite que o dono escreveu e' COMPORTAMENTAL ("dado o cenario da v1.0, a skill tem
de parar em tres pontos"), e comportamento de modelo nao roda em canario local. Entao este arquivo
NAO promete provar comportamento. Ele prova o que da' para provar por leitura:

  (a) as cinco travas da §1 existem, com o texto que as torna condicao de parada;
  (b) as seis alteracoes de passo existem;
  (c) o §12 (onde mora a configuracao) nao tem ponteiro morto;
  (d) o nucleo nao hardcoda norma regulatoria (ADR-010/020);
  (e) o numero que a prosa afirma sobre os multiplicadores BATE com a tabela do proprio arquivo.

O item (e) e' o unico que mede em vez de procurar palavra, e e' o que pegou o defeito real: a
versao recebida afirmava "quatro fatores no piso ja dao 1,8" quando a tabela produz no maximo
1,7457. Prosa auditada contra o mecanismo que ela descreve — mesmo desenho de test_numeros_controle.

O QUE ESTE CANARIO NAO COBRE, dito de proposito: se a skill de fato REPROVA a v1.0 do caso H-01.
Isso e' execucao de modelo, fica como evidencia datada no ADR-114, nao como gate continuo.
Prometer cobertura que o mecanismo nao tem foi o defeito que o QA da rodada 3 do ADR-113 achou.
"""
import os
import re
import sys
from itertools import combinations
from math import prod

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(RAIZ, "_shared", "service-valuation", "SKILL.md")
EXEMPLO = os.path.join(RAIZ, "exemplos", "service-valuation", "RATE-CARD.example.md")
TEMPLATE = os.path.join(RAIZ, "_shared", "service-valuation", "TEMPLATE-MEMORIA-CALCULO.md")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

falhas = []


def checar(desc, cond, dica=""):
    print(f"  {'ok  ' if cond else 'FAIL'} {desc}" + ("" if cond else f" {dica}"))
    if not cond:
        falhas.append(desc)


def ler(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


print("Os arquivos existem?")
for p in (SKILL, EXEMPLO, TEMPLATE):
    checar(os.path.relpath(p, RAIZ), os.path.isfile(p))
if falhas:
    print("\nFAIL — sem os arquivos nao ha o que auditar.")
    sys.exit(1)

texto = ler(SKILL)

print("\nAs cinco travas da §1 existem? (regras 7 a 11 — ADR-114)")
TRAVAS = {
    "7 retrabalho do fornecedor sai do faturavel": r"Retrabalho do fornecedor n[ãa]o [ée] entrega",
    "8 faixa de unidade e' TRAVA": r"Faixa de unidade [ée] TRAVA",
    "9 sem fonte independente a Lente B nao existe": r"Sem fonte independente, a Lente B n[ãa]o existe",
    "10 teto indeterminado nao autoriza preco": r"Teto indeterminado n[ãa]o autoriza pre[çc]o",
    "11 teste do espanto": r"Teste do espanto",
}
for nome, pad in TRAVAS.items():
    checar(nome, re.search(pad, texto) is not None)

print("\nAs travas sao condicao de PARADA, nao sugestao?")
# uma trava que nao diz o que acontece ao ser violada e' decorativa
checar("a faixa de unidade diz que INVALIDA a valoracao",
       "invalida a valoração" in texto,
       "-> sem consequencia escrita, 'trava' e' so uma palavra mais forte para 'sugestao'")
checar("a Lente B sem fonte vira faixa, NUNCA ponto",
       re.search(r"\*\*faixa\*\*, nunca ponto", texto) is not None)
checar("o teste do espanto poe o erro no numero, nao no cliente",
       re.search(r"o n[úu]mero est[áa] errado — n[ãa]o o cliente", texto) is not None)

print("\nAs seis alteracoes de passo existem?")
PASSOS = {
    "Passo 1: linha de codigo nao e' ancora de ESFORCO": r"nem como [âa]ncora\s*\n?de\s*esfor[çc]o|nem como [âa]ncora de esfor[çc]o",
    "Passo 2: F-nn (excluido: retrabalho)": r"F-nn \(exclu[íi]do: retrabalho\)",
    "Passo 4: quanto custaria comprar o RESULTADO pronto": r"RESULTADO pronto",
    "Passo 6: escassez exige FONTE": r"Escass[ãa-z]* exige FONTE|Escassez exige FONTE",
    "Passo 6: reversibilidade e' de negocio, nao de log": r"Reversibilidade [ée] de neg[óo]cio, n[ãa]o de log",
    "Passo 7: quarta linha 'Teto indeterminado'": r"\*\*Teto indeterminado\*\* \|",
}
for nome, pad in PASSOS.items():
    checar(nome, re.search(pad, texto, re.S) is not None)

print("\nO checklist adversarial do Passo 8 ganhou os itens novos?")
bloco8 = texto.split("## 10. Passo 8")[-1].split("## 11.")[0] if "## 10. Passo 8" in texto else ""
itens = re.findall(r"^- \[ \]", bloco8, re.M)
checar(f"o checklist tem itens marcaveis (achados: {len(itens)})", len(itens) >= 8,
       "-> o ADR-114 declara oito itens novos de checklist adversarial")

print("\nO §12 tem ponteiro morto? (onde mora a configuracao)")
checar("o §12 existe", "## 12." in texto)
sec12 = texto.split("## 12.")[-1].split("## 13.")[0]
checar("o §12 aponta o exemplo do repositorio",
       "exemplos/service-valuation/RATE-CARD.example.md" in sec12)
checar("o caminho que ele aponta EXISTE de fato", os.path.isfile(EXEMPLO),
       "-> ponteiro para arquivo inexistente e' defeito, nao estilo")
checar("o §12 diz o que fazer quando NENHUMA config existe",
       "[DESCONHECIDO]" in sec12 and "não um preço" in sec12,
       "-> sem isso a skill sem rate card inventa taxa, que e' o pior dos mundos")
_exemplo = ler(EXEMPLO)
checar("o exemplo publico nao tem taxa de verdade em TABELA",
       not re.search(r"\|\s*\d{2,4}\s*\|\s*\d{2,4}\s*\|", _exemplo),
       "-> o exemplo existe justamente para NAO carregar numero")

# Achado MEDIA do QA (23a rodada): a checagem acima so' olhava LINHA DE TABELA.
# Uma frase em prosa — "consultor senior custa R$ 300/hora" — passava inteira,
# e e' a forma mais natural de alguem colar um numero real ao editar o exemplo.
# Valor monetario e taxa horaria sao o que este arquivo existe para NAO ter.
_EM_PROSA = (
    r"R\$\s*\d",                          # R$ 300
    r"\d+\s*(?:reais|dolares|dólares)",    # 300 reais
    r"\d+\s*/\s*(?:h|hora)\b",           # 300/h, 300 / hora
    r"\bUS\$\s*\d",
    # Os DOIS escapes REAIS, medidos pelo critico da 24a rodada contra sete
    # frases: codigo ISO de moeda ("300 BRL") e taxa por unidade que nao
    # seja hora ("2.400/dia", sem marcador de moeda). Diaria e' mais comum
    # que hora em rate card de consultoria, e o padrao anterior so' cobria
    # `/h|hora`.
    #
    # NAO entrou, e a distincao importa: separador de milhar. Eu levantei
    # como suspeita e o critico MEDIU — "1.500,00 reais" ja' era capturado,
    # porque a palavra "reais" ancora. Apontar isso como gap seria teatro.
    #
    # SEGUE ESCAPANDO, declarado: numero por extenso ("trezentos reais").
    # Cobrir exigiria dicionario de grafias, e a fronteira de onde parar e'
    # arbitraria. O `por_extenso` da vitrine existe porque LA' o numero e'
    # gerado por nos; aqui seria adivinhar o que um humano escreveu.
    r"\d+\s*/\s*(?:dia|semana|m[êe]s|ano)\b",
    r"\d+\s*(?:BRL|USD|EUR)\b",
)
_achados = [m.group(0) for padrao in _EM_PROSA
            for m in re.finditer(padrao, _exemplo, re.I)]
checar("o exemplo publico nao tem taxa de verdade em PROSA",
       not _achados,
       f"-> valor colado fora de tabela tambem vaza: {_achados[:5]}")

print("\nO nucleo continua agnostico? (ADR-010/020 — a norma e' declarada pelo projeto)")
for norma in ("ANVISA", "GxP", "SOX", "LGPD", "FDA", "21 CFR"):
    checar(f"sem '{norma}' hardcoded", norma not in texto,
           "-> norma no nucleo viaja para projeto que nao e' regulado")
checar("o eixo Ambiente delega a norma ao projeto",
       re.search(r"o projeto declara qual norma", texto) is not None)

print("\nO numero da prosa bate com a TABELA do proprio arquivo?")
# le os pisos da tabela de multiplicadores do Passo 6: '| Fator | 1,15 a 1,40 | ... |'
pisos = []
for linha in texto.splitlines():
    m = re.match(r"^\|[^|]+\|\s*(\d,\d{2})\s+a\s+(\d,\d{2})\s*\|", linha)
    if m:
        piso = float(m.group(1).replace(",", "."))
        if piso >= 1.0:                      # 0,60 a 0,85 e' redutor: nao empilha para cima
            pisos.append(piso)
checar(f"a tabela de multiplicadores foi lida (fatores que aumentam: {len(pisos)})", len(pisos) >= 4,
       "-> se a tabela mudou de formato, este canario para de medir e vira decoracao")

if len(pisos) >= 4:
    maior4 = max(prod(c) for c in combinations(pisos, 4))
    esperado = f"{maior4:.2f}".replace(".", ",")
    # [ACHADO NA PROVA DE MUTACAO] a primeira versao checava `esperado in texto` — presenca em
    # QUALQUER lugar. Como a prosa cita o numero duas vezes, plantar o valor errado numa das duas
    # deixava a outra e o canario passava: prosa CONTRADITORIA saia verde. Agora a checagem ancora
    # na frase que faz a AFIRMACAO (quatro ... piso ... numero) e compara aquele numero.
    afirmacoes = re.findall(r"[Qq]uatro[^.]{0,160}?[Pp][Ii][Ss][Oo][^.]{0,160}?(\d,\d{1,2})", texto)
    checar("a afirmacao sobre quatro pisos foi encontrada (senao esta checagem e' decoracao)",
           len(afirmacoes) >= 1,
           "-> se a frase mudou de forma, o canario parou de medir; reancore o padrao")
    ruins = [a for a in afirmacoes if a != esperado]
    checar(f"toda afirmacao sobre quatro pisos cita o maximo REAL ({esperado})",
           not ruins,
           f"-> afirmam {ruins}; medido {maior4:.4f} da tabela deste mesmo arquivo. "
           f"A versao recebida de fora dizia 1,8, e a tabela nao produz isso")
    teto = re.search(r"Teto do produto: (\d,\d{2})", texto)
    checar("o teto do produto esta declarado", teto is not None)
    if teto:
        v = float(teto.group(1).replace(",", "."))
        checar(f"quatro pisos ({maior4:.2f}) de fato estouram o teto ({v:.2f})", maior4 > v,
               "-> se nao estourassem, o argumento da secao seria falso")

print("\nToda razao 'Nx' afirmada sobre o caso carrega a conta, e a conta fecha?")
# [ACHADO ALTA DO QA DO ADR-114] o material de origem dizia "28x no preco" e o autor propagou para
# CINCO arquivos sem fazer a divisao: 270.000/13.000 = 20,8. Numero sem origem, que e' o que a
# Regra 1 da propria skill proibe. A correcao nao foi so trocar o valor: a prosa passa a exibir a
# divisao ao lado da razao, e este canario confere a aritmetica. Alegacao que carrega a propria
# prova e' auditavel; alegacao nua depende de alguem lembrar de conferir.
DOCS_RAZAO = [
    os.path.join(RAIZ, "docs", "adr",
                 "114-valoracao-de-servico-entra-no-nucleo-calibrada-por-caso-real.md"),
    os.path.join(RAIZ, "docs", "_private", "service-valuation", "HISTORICO-ENTREGAS.md"),
    os.path.join(RAIZ, "CHANGELOG.md"),
]
PAD_RAZAO = re.compile(r"(\d+,\d+)x[^(\n]{0,40}?\(\s*([\d.]+)\s*÷\s*([\d.]+)\s*\)")
total_razoes = 0
for doc in DOCS_RAZAO:
    if not os.path.isfile(doc):
        continue
    for m in PAD_RAZAO.finditer(ler(doc)):
        total_razoes += 1
        alegado = float(m.group(1).replace(",", "."))
        a = float(m.group(2).replace(".", ""))
        b = float(m.group(3).replace(".", ""))
        real = a / b
        nome = os.path.basename(doc)
        checar(f"{nome}: {m.group(1)}x = {m.group(2)}/{m.group(3)}",
               abs(alegado - real) < 0.05,
               f"-> a conta da' {real:.2f}; a prosa afirma {alegado}. "
               f"Foi assim que o '28x' sobreviveu em cinco arquivos")
checar(f"as razoes com conta a' vista foram encontradas (achadas: {total_razoes})",
       total_razoes >= 4,
       "-> se a prosa parou de exibir a divisao, este canario parou de medir e virou decoracao")

print("\nO QUE ESTE CANARIO NAO COBRE, dito de proposito: se a skill REPROVA a v1.0 do caso H-01.")
print("Isso exige rodar um modelo. Fica como evidencia datada no ADR-114, nao como gate continuo.")

if falhas:
    print(f"\nFAIL — {len(falhas)} verificacao(oes) falharam: {falhas}")
    sys.exit(1)
print("\nPASS — as travas existem, o §12 nao tem ponteiro morto, e o numero fecha com a tabela.")
sys.exit(0)
