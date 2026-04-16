import sys
from antlr4 import CommonTokenStream, InputStream
from NoQLLexer  import NoQLLexer
from NoQLParser import NoQLParser

OK  = "\033[92m\033[0m"
ERR = "\033[91m\033[0m"

def parsear(codigo: str):
    stream = InputStream(codigo)
    lexer  = NoQLLexer(stream)
    tokens = CommonTokenStream(lexer)
    parser = NoQLParser(tokens)

    # Capturar errores
    errores = []
    class ColectorErrores:
        def syntaxError(self, recognizer, offendingSymbol, line, col, msg, e):
            errores.append(f"línea {line}:{col} → {msg}")
        def reportAmbiguity(self, *a): pass
        def reportAttemptingFullContext(self, *a): pass
        def reportContextSensitivity(self, *a): pass

    from antlr4 import DiagnosticErrorListener
    parser.removeErrorListeners()
    parser.addErrorListener(ColectorErrores())

    arbol = parser.programa()
    return arbol, errores

CASOS = [
    # (nombre, código, debe_pasar)
    (
        "INSERT simple",
        'INSERT INTO usuarios VALUES {"nombre": "Ana", "edad": 30}',
        True,
    ),
    (
        "INSERT con documento vacío",
        'INSERT INTO logs VALUES {}',
        True,
    ),
    (
        "FIND sin filtro",
        'FIND IN productos',
        True,
    ),
    (
        "FIND con WHERE simple",
        'FIND IN productos WHERE precio > 100',
        True,
    ),
    (
        "FIND con WHERE y LIMIT",
        'FIND IN pedidos WHERE estado == "activo" LIMIT 10',
        True,
    ),
    (
        "UPDATE con WHERE",
        'UPDATE usuarios SET edad = 31 WHERE nombre == "Ana"',
        True,
    ),
    (
        "UPDATE múltiples campos",
        'UPDATE config SET version = 2, activo = TRUE',
        True,
    ),
    (
        "DELETE con WHERE",
        'DELETE FROM usuarios WHERE edad < 18',
        True,
    ),
    (
        "DELETE sin WHERE",
        'DELETE FROM temporales',
        True,
    ),
    (
        "Condición AND",
        'FIND IN empleados WHERE departamento == "TI" AND salario >= 3000',
        True,
    ),
    (
        "Condición OR",
        'FIND IN clientes WHERE ciudad == "Bogotá" OR ciudad == "Medellín"',
        True,
    ),
    (
        "Condición NOT",
        'FIND IN items WHERE NOT activo == TRUE',
        True,
    ),
    (
        "Documento anidado",
        '''INSERT INTO ordenes VALUES {
            "id": 1,
            "cliente": {"nombre": "Luis", "ciudad": "Bogotá"},
            "items": ["lapiz", "cuaderno"]
        }''',
        True,
    ),
    (
        "Múltiples sentencias",
        '''INSERT INTO col VALUES {"x": 1}
           FIND IN col WHERE x == 1
           DELETE FROM col WHERE x == 1''',
        True,
    ),
    (
        "Falta VALUES",
        'INSERT INTO usuarios {"nombre": "Error"}',
        False,
    ),
    (
        "Operador inválido",
        'FIND IN col WHERE edad === 30',
        False,
    ),
]

def main():
    print("  PRUEBAS PARSER NoQL (ANTLR4)")

    aprobados = 0
    for nombre, codigo, debe_pasar in CASOS:
        arbol, errores = parsear(codigo)
        paso = len(errores) == 0

        if paso == debe_pasar:
            icono = OK
            aprobados += 1
        else:
            icono = ERR

        print(f"\n{icono} {nombre}")
        if errores:
            for e in errores:
                print(f"{e}")
        elif debe_pasar:
            print(f"{arbol.toStringTree(recog=None)[:80]}…")

    print(f"  Resultado: {aprobados}/{len(CASOS)} pruebas pasaron")

if __name__ == "__main__":
    main()
