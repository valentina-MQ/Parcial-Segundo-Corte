import re, sys
from dataclasses import dataclass, field
from typing import Any


TOKEN_RE = re.compile(
    r'\d+(?:\.\d+)?'           #Números
    r'|[+\-*/(){}=!<>]+'       #Operadores y símbolos
    r'|[a-zA-Z_]\w*'           #Identificadores / palabras clave
    r'|\S'                     #Cualquier otro carácter no-espacio
)
KEYWORDS = {'if', 'elif', 'else', 'true', 'false'}

@dataclass
class Token:
    tipo: str
    valor: str
    linea: int = 0

def lexer(codigo: str) -> list[Token]:
    tokens = []
    for linea_n, linea in enumerate(codigo.splitlines(), 1):
        for m in TOKEN_RE.finditer(linea):
            val = m.group()
            if re.fullmatch(r'\d+(?:\.\d+)?', val):
                tipo = 'NUM'
            elif val in KEYWORDS:
                tipo = val.upper()
            elif re.fullmatch(r'[a-zA-Z_]\w*', val):
                tipo = 'ID'
            elif val in ('==','!=','<=','>=','<','>'):
                tipo = 'COMP'
            elif val == '=':
                tipo = 'ASIG'
            elif val in ('+','-','*','/','(',')','{','}'):
                tipo = val
            else:
                raise SyntaxError(f"Token desconocido: '{val}' en línea {linea_n}")
            tokens.append(Token(tipo, val, linea_n))
    tokens.append(Token('EOF', '', 0))
    return tokens

#Nodos pal AST
@dataclass
class NodoNum:        valor: float
@dataclass
class NodoId:         nombre: str
@dataclass
class NodoBinOp:      op: str; izq: Any; der: Any
@dataclass
class NodoAsig:       nombre: str; expr: Any
@dataclass
class NodoBloque:     sentencias: list
@dataclass
class NodoIf:
    condicion:  Any
    bloque_si:  Any
    elif_ramas: list        #[(cond, bloque), ...]
    bloque_no:  Any = None


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def actual(self) -> Token:
        return self.tokens[self.pos]

    def mirar(self, offset=0) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def emparejar(self, tipo: str) -> Token:
        tok = self.actual()

        if tok.tipo != tipo:
            raise SyntaxError(
                f"Línea {tok.linea}: se esperaba '{tipo}' "
                f"pero se encontró '{tok.valor}' ({tok.tipo})"
            )
        self.pos += 1
        return tok

    def verificar(self, *tipos) -> bool:
        return self.actual().tipo in tipos

    def parse_programa(self) -> NodoBloque:
        stmts = []
        while not self.verificar('EOF'):
            stmts.append(self.parse_sentencia())
        return NodoBloque(stmts)

    def parse_sentencia(self):
        #Asignación: ID '=' expr
        if self.verificar('ID') and self.mirar(1).tipo == 'ASIG':
            return self.parse_asignacion()
        #Condicional
        elif self.verificar('IF'):
            return self.parse_condicional()
        #Expresión
        else:
            return self.parse_expresion()

    def parse_asignacion(self) -> NodoAsig:
        nombre = self.emparejar('ID').valor
        self.emparejar('ASIG')
        expr = self.parse_expresion()
        return NodoAsig(nombre, expr)

    def parse_condicional(self) -> NodoIf:
        self.emparejar('IF')
        self.emparejar('(')
        cond = self.parse_expresion()
        self.emparejar(')')
        bloque_si = self.parse_bloque()

        elif_ramas = []
        while self.verificar('ELIF'):
            self.emparejar('ELIF')
            self.emparejar('(')
            c = self.parse_expresion()
            self.emparejar(')')
            b = self.parse_bloque()
            elif_ramas.append((c, b))

        bloque_no = None
        if self.verificar('ELSE'):
            self.emparejar('ELSE')
            bloque_no = self.parse_bloque()

        return NodoIf(cond, bloque_si, elif_ramas, bloque_no)

    def parse_bloque(self) -> NodoBloque:
        self.emparejar('{')
        stmts = []
        while not self.verificar('}', 'EOF'):
            stmts.append(self.parse_sentencia())
        self.emparejar('}')
        return NodoBloque(stmts)

    def parse_expresion(self):
        return self.parse_comparacion()

    def parse_comparacion(self):
        izq = self.parse_suma()
        while self.verificar('COMP'):
            op = self.emparejar('COMP').valor
            der = self.parse_suma()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_suma(self):
        izq = self.parse_termino()
        while self.verificar('+', '-'):
            op = self.actual().tipo
            self.pos += 1
            der = self.parse_termino()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_termino(self):
        izq = self.parse_factor()
        while self.verificar('*', '/'):
            op = self.actual().tipo
            self.pos += 1
            der = self.parse_factor()
            izq = NodoBinOp(op, izq, der)
        return izq

    def parse_factor(self):
        tok = self.actual()
        if tok.tipo == 'NUM':
            self.pos += 1
            return NodoNum(float(tok.valor))
        elif tok.tipo == 'ID':
            self.pos += 1
            return NodoId(tok.nombre if hasattr(tok, 'nombre') else tok.valor)
        elif tok.tipo == '(':
            self.emparejar('(')
            expr = self.parse_expresion()
            self.emparejar(')')
            return expr
        else:
            raise SyntaxError(
                f"Línea {tok.linea}: factor inesperado '{tok.valor}'"
            )


class Interprete:
    def __init__(self):
        self.env: dict = {}

    def evaluar(self, nodo) -> Any:
        match nodo:
            case NodoNum(valor=v):
                return v
            case NodoId(nombre=n):
                if n not in self.env:
                    raise NameError(f"Variable no definida: '{n}'")
                return self.env[n]
            case NodoBinOp(op=op, izq=izq, der=der):
                l, r = self.evaluar(izq), self.evaluar(der)
                return {'+': l+r, '-': l-r, '*': l*r, '/': l/r,
                        '==': l==r, '!=': l!=r, '<': l<r,
                        '>': l>r, '<=': l<=r, '>=': l>=r}[op]
            case NodoAsig(nombre=n, expr=e):
                self.env[n] = self.evaluar(e)
                return self.env[n]
            case NodoBloque(sentencias=ss):
                resultado = None
                for s in ss: resultado = self.evaluar(s)
                return resultado
            case NodoIf(condicion=c, bloque_si=si, elif_ramas=elifs, bloque_no=no):
                if self.evaluar(c):
                    return self.evaluar(si)
                for (ec, eb) in elifs:
                    if self.evaluar(ec):
                        return self.evaluar(eb)
                if no:
                    return self.evaluar(no)

def ejecutar(codigo: str) -> dict:
    toks = lexer(codigo)
    ast  = Parser(toks).parse_programa()
    interp = Interprete()
    interp.evaluar(ast)
    return interp.env


if __name__ == '__main__':
    programas = [
        ("Asignaciones básicas", """
            x = 10
            y = 20
            z = x + y * 2
        """),
        ("Condicional simple", """
            a = 5
            if (a > 3) {
                b = 1
            } else {
                b = 0
            }
        """),
        ("Condicional con elif", """
            nota = 75
            if (nota >= 90) {
                grado = 5
            } elif (nota >= 70) {
                grado = 4
            } elif (nota >= 60) {
                grado = 3
            } else {
                grado = 2
            }
        """),
        ("Expresiones complejas", """
            pi = 3
            r = 7
            area = pi * r * r
            grande = 0
            if (area >= 100) {
                grande = 1
            }
        """),
    ]

    for nombre, codigo in programas:
        try:
            env = ejecutar(codigo)
            vars_str = ', '.join(f"{k}={v}" for k, v in env.items())
            print(f"{nombre}: {vars_str}")
        except Exception as e:
            print(f"{nombre}: {e}")