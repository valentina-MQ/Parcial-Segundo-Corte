import time, re, sys
from itertools import product as iproduct
import random

def tokenize(expr: str) -> list[str]:
    tokens = re.findall(r'\d+(?:\.\d+)?|[+\-*/()]', expr.replace(' ', ''))
    return tokens


#Producciones binarias:  (A → B C)
BIN_PRODS = [
    ('E',  'E',  'AO'),
    ('E',  'E_',  'T'),   #E_ es alias de E en recursión derecha
    ('T',  'T',  'MO'),
    ('T',  'T_', 'F'),
    ('F',  'LP', 'ER'),
    ('ER', 'E',  'RP'),
]

#Producciones unitarias terminales: (A → token)
def terminal_tags(tok: str) -> list[str]:
    tags = []
    if re.fullmatch(r'\d+(?:\.\d+)?', tok):
        tags += ['NUM', 'F', 'T', 'E']
    if tok in ('+', '-'):
        tags += ['AO']
    if tok in ('*', '/'):
        tags += ['MO']
    if tok == '(':
        tags += ['LP']
    if tok == ')':
        tags += ['RP']
    return tags

def cyk_parse(tokens: list[str]) -> bool:
    n = len(tokens)
    #tabla[i][j] = conjunto de no-terminales que generan tokens[i..j]
    tabla = [[set() for _ in range(n)] for _ in range(n)]

    #Inicializar diagonal (longitud 1)
    for i, tok in enumerate(tokens):
        tabla[i][i] = set(terminal_tags(tok))

    #Llenar para longitudes 2..n
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                for (A, B, C) in BIN_PRODS:
                    if B in tabla[i][k] and C in tabla[k+1][j]:
                        tabla[i][j].add(A)

    return 'E' in tabla[0][n - 1]


def cyk_eval(tokens: list[str]) -> float:
    return ll_eval(tokens)

TABLA_LL = {
    'E' : {
        'num': ['T', "E'"],
        '('  : ['T', "E'"],
    },
    "E'": {
        '+'  : ['+', 'T', "E'"],
        '-'  : ['-', 'T', "E'"],
        ')'  : [],          # ε
        '$'  : [],          # ε
    },
    'T' : {
        'num': ['F', "T'"],
        '('  : ['F', "T'"],
    },
    "T'": {
        '*'  : ['*', 'F', "T'"],
        '/'  : ['/', 'F', "T'"],
        '+'  : [],  '-': [], ')': [], '$': [],
    },
    'F' : {
        'num': ['num'],
        '('  : ['(', 'E', ')'],
    },
}

def ll_token_type(tok: str) -> str:
    if re.fullmatch(r'\d+(?:\.\d+)?', tok):
        return 'num'
    return tok

def ll_recognize(tokens: list[str]) -> bool:
    entrada = tokens + ['$']
    pila = ['$', 'E']
    i = 0
    while pila[-1] != '$':
        tope = pila[-1]
        tok_type = ll_token_type(entrada[i])
        if tope == tok_type or (tope == 'num' and tok_type == 'num'):
            pila.pop(); i += 1
        elif tope in TABLA_LL:
            prod = TABLA_LL[tope].get(tok_type)
            if prod is None:
                return False
            pila.pop()
            for s in reversed(prod):
                if s:
                    pila.append(s)
        else:
            return False
    return entrada[i] == '$'

def ll_eval(tokens: list[str]) -> float:
    pos = [0]
    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else '$'
    def consume():
        t = tokens[pos[0]]; pos[0] += 1; return t

    def parse_E():
        val = parse_T()
        while peek() in ('+', '-'):
            op = consume()
            r = parse_T()
            val = val + r if op == '+' else val - r
        return val

    def parse_T():
        val = parse_F()
        while peek() in ('*', '/'):
            op = consume()
            r = parse_F()
            val = val * r if op == '*' else val / r
        return val

    def parse_F():
        t = peek()
        if t == '(':
            consume()
            val = parse_E()
            consume()  # ')'
            return val
        else:
            return float(consume())

    return parse_E()

def generar_expresion(profundidad: int) -> str:
    if profundidad == 0 or random.random() < 0.3:
        return str(random.randint(1, 99))
    op = random.choice(['+', '-', '*', '/'])
    izq = generar_expresion(profundidad - 1)
    der = generar_expresion(profundidad - 1)
    return f"({izq} {op} {der})"

def benchmark(n_pruebas=500, profundidad=4):
    print(f"\nBENCHMARK: {n_pruebas} expresiones, profundidad {profundidad}")

    expresiones = [generar_expresion(profundidad) for _ in range(n_pruebas)]
    tokens_list  = [tokenize(e) for e in expresiones]

    #CYK
    t0 = time.perf_counter()
    for toks in tokens_list:
        cyk_parse(toks)
    t_cyk = time.perf_counter() - t0

    #LL(1)
    t0 = time.perf_counter()
    for toks in tokens_list:
        ll_recognize(toks)
    t_ll = time.perf_counter() - t0

    #Resultados
    lens = [len(t) for t in tokens_list]
    print(f"  Longitud promedio de tokens : {sum(lens)/len(lens):.1f}")
    print(f"  Tiempo total CYK            : {t_cyk*1000:.2f} ms")
    print(f"  Tiempo total LL(1)          : {t_ll*1000:.2f} ms")
    print(f"  Tiempo promedio CYK         : {t_cyk/n_pruebas*1e6:.2f} µs/expr")
    print(f"  Tiempo promedio LL(1)       : {t_ll/n_pruebas*1e6:.2f} µs/expr")
    print(f"  Razón CYK/LL(1)             : {t_cyk/t_ll:.1f}x más lento")
    print()



CASOS = [
    ("2 + 3",              5.0),
    ("10 - 4 * 2",         2.0),
    ("(10 - 4) * 2",      12.0),
    ("3 + 4 * 2 / (1-5)", -2.0 + 3),   # 3 + 4*2/(−4) = 3−2 = 1 → ajustado abajo
    ("100 / 5 / 4",        5.0),
    ("2 * (3 + (4 - 1))", 12.0),
]
#corrección del caso 4: 3 + 4*2/(1-5) = 3 + 8/(-4) = 3 - 2 = 1
CASOS[3] = ("3 + 4 * 2 / (1 - 5)", 1.0)

def pruebas_funcionales():
    print("PRUEBAS FUNCIONALES")
    print(f"  {'Expresión':<30} {'Esperado':>10} {'CYK':>8} {'LL(1)':>8} {'OK':>4}")
    print("  " + "-"*62)
    for expr, esperado in CASOS:
        toks = tokenize(expr)
        acepta_cyk = cyk_parse(toks)
        valor_ll   = ll_eval(toks)
        ok = "Okis" if abs(valor_ll - esperado) < 1e-9 and acepta_cyk else "Noks"
        print(f"  {expr:<30} {esperado:>10.2f} {'✓' if acepta_cyk else '✗':>8} "
              f"{valor_ll:>8.2f} {ok:>4}")

if __name__ == '__main__':
    pruebas_funcionales()
    benchmark(n_pruebas=300, profundidad=3)
    benchmark(n_pruebas=100, profundidad=5)