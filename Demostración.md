# Punto 3: Ambigüedad de la gramática if-then-else

## Demostración de ambigüedad

La gramática propuesta sigue siendo ambigua. Considera esta entrada:

```
if e1 then if e2 then if e3 then p1 else p2
```

Con la gramática dada se pueden construir dos árboles distintos:

### Árbol 1 — el `else` se empareja con el segundo `if`:

```
prop
└── if e1 then prop
              └── prop_emparejada
                  └── if e2 then prop_emparejada else prop
                                 └── if e3 then p1        └── p2
```

### Árbol 2 — el `else` se empareja con el tercer `if`:

```
prop
└── if e1 then prop
              └── prop_emparejada
                  └── if e2 then prop_emparejada else prop
                                 └── ???   (no puede derivar if e3 then p1 else p2 aquí)
```

El problema central es que:

```
prop_emparejada --> if expr then prop_emparejada else prop
```

permite que la `prop` del `then` sea no emparejada, lo que deja abierta la posibilidad de múltiples emparejamientos del `else`.

---

## Gramática corregida (no ambigua)

La solución clásica es exigir que en todos los `then` de una `prop_emparejada`, las subproposiciones también sean emparejadas:

```
prop             --> if expr then prop
                   | prop_emparejada

prop_emparejada  --> if expr then prop_emparejada else prop_emparejada
                   | otras
```

### Cambio clave

En la regla de `prop_emparejada`, el `else` ahora lleva `prop_emparejada` (no `prop`).

Esto garantiza que cada `else` se asocia siempre al `if` más cercano que no tenga aún un `else`, eliminando la ambigüedad.
