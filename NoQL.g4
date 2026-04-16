grammar NoQL;

// ─── PARSER ───────────────────────────────────────────────────

programa
    : sentencia+ EOF
    ;

sentencia
    : insertar
    | buscar
    | actualizar
    | eliminar
    ;

// CREATE
insertar
    : INSERT INTO coleccion VALUES documento
    ;

// READ
buscar
    : FIND IN coleccion (WHERE condicion)? (LIMIT NUMERO)?
    ;

// UPDATE
actualizar
    : UPDATE coleccion SET asignaciones (WHERE condicion)?
    ;

// DELETE
eliminar
    : DELETE FROM coleccion (WHERE condicion)?
    ;

documento
    : '{' campos '}'
    | '{' '}'
    ;

campos
    : campo (',' campo)*
    ;

campo
    : clave ':' valor
    ;

asignaciones
    : asignacion (',' asignacion)*
    ;

asignacion
    : clave '=' valor
    ;

// Condiciones con precedencia: NOT > AND > OR
condicion
    : condicion OR  condicion                   # condOr
    | condicion AND condicion                   # condAnd
    | NOT condicion                             # condNot
    | '(' condicion ')'                         # condGrupo
    | clave operador valor                      # condCmp
    ;

operador
    : EQ | NEQ | LT | GT | LTE | GTE
    ;

valor
    : NUMERO                                    # valNum
    | CADENA                                    # valCad
    | booleano                                  # valBool
    | documento                                 # valDoc
    | arreglo                                   # valArr
    | NULL                                      # valNull
    ;

arreglo
    : '[' (valor (',' valor)*)? ']'
    ;

booleano
    : TRUE
    | FALSE
    ;

// Ajuste clave: Ahora acepta "nombre" (CADENA) o nombre (ID)
clave     : ID | CADENA ;
coleccion : ID ;

// ─── LEXER ────────────────────────────────────────────────────

INSERT  : 'INSERT' ;
INTO    : 'INTO'   ;
VALUES  : 'VALUES' ;
FIND    : 'FIND'   ;
IN      : 'IN'     ;
WHERE   : 'WHERE'  ;
LIMIT   : 'LIMIT'  ;
UPDATE  : 'UPDATE' ;
SET     : 'SET'    ;
DELETE  : 'DELETE' ;
FROM    : 'FROM'   ;
AND     : 'AND'    ;
OR      : 'OR'     ;
NOT     : 'NOT'    ;
TRUE    : 'TRUE'   ;
FALSE   : 'FALSE'  ;
NULL    : 'NULL'   ;

EQ  : '==' ;
NEQ : '!=' ;
LTE : '<=' ;
GTE : '>=' ;
LT  : '<'  ;
GT  : '>'  ;

ID : [a-zA-Z_][a-zA-Z0-9_]* ;

NUMERO : '-'? [0-9]+ ('.' [0-9]+)? ;

CADENA : '"' (~["\r\n])* '"' ;

WS : [ \t\r\n]+ -> skip ;