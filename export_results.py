#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ejecuta las consultas de sales_analysis.sql y exporta sus resultados a JSON.

Las consultas NO se copian aqui: se leen del propio .sql y se ejecutan sobre
el mismo CSV que publica el repositorio. Si alguien cambia una consulta, el
panel cambia con ella; una copia pegada en este script acabaria, tarde o
temprano, ensennando un numero que la consulta ya no da.

El motor es SQLite porque es lo que el .sql ya asume: usa strftime(), que no
existe en PostgreSQL.

    python3 export_results.py [directorio_de_salida]
"""
import csv
import json
import os
import sqlite3
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(AQUI, 'sales_data.csv')
SQL = os.path.join(AQUI, 'sales_analysis.sql')

# El orden es el del fichero .sql; el nombre es el del JSON que se genera.
NOMBRES = [
    'regiones',
    'top_vendedores',
    'clientes_por_categoria',
    'tendencia_mensual',
    'margen_bajo',
]

NUMERICAS = ('Revenue', 'Cost', 'Profit')


def cargar(con):
    """Mete el CSV en una tabla, con los importes como numeros."""
    with open(CSV, newline='', encoding='utf-8') as f:
        filas = list(csv.DictReader(f))
    if not filas:
        sys.exit('El CSV esta vacio')

    campos = list(filas[0].keys())
    tipos = ', '.join(
        '%s %s' % (c, 'REAL' if c in NUMERICAS else 'TEXT') for c in campos
    )
    con.execute('CREATE TABLE sales_data (%s)' % tipos)
    con.executemany(
        'INSERT INTO sales_data VALUES (%s)' % ','.join('?' * len(campos)),
        [[float(r[c]) if c in NUMERICAS else r[c] for c in campos] for r in filas],
    )
    return len(filas)


def consultas():
    """Las sentencias del .sql, sin los comentarios, en orden.

    Hay que cortar el comentario que va DETRAS del punto y coma, no solo las
    lineas que empiezan por guiones: la ultima consulta termina en
    "< 1000; -- Asumiendo que...", y al partir por el punto y coma ese
    comentario se convertia en una sexta consulta fantasma.

    Vale mientras ningun literal de texto contenga dos guiones seguidos.
    """
    crudo = open(SQL, encoding='utf-8').read()
    limpio = '\n'.join(l.split('--')[0] for l in crudo.splitlines())
    return [q.strip() for q in limpio.split(';') if q.strip()]


def redondear(v):
    return round(v, 2) if isinstance(v, float) else v


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'resultados')
    os.makedirs(salida, exist_ok=True)

    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    n = cargar(con)
    print('filas cargadas: %d' % n)

    qs = consultas()
    if len(qs) != len(NOMBRES):
        sys.exit('El .sql tiene %d consultas y aqui hay %d nombres: '
                 'anade el nombre de la nueva antes de seguir.' % (len(qs), len(NOMBRES)))

    for nombre, q in zip(NOMBRES, qs):
        filas = [{k: redondear(r[k]) for k in r.keys()} for r in con.execute(q)]
        destino = os.path.join(salida, nombre + '.json')
        with open(destino, 'w', encoding='utf-8') as f:
            json.dump(filas, f, ensure_ascii=False, indent=1)
        print('  %-24s %2d filas -> %s' % (nombre, len(filas), os.path.basename(destino)))
        if not filas:
            print('     ^ SIN RESULTADOS: la demo tiene que decirlo, no dejar el hueco')

    # Cabecera del panel. Sale de la misma tabla, no de sumar los JSON de
    # arriba: la consulta 5 filtra con HAVING y sumar sus filas daria otro total.
    k = con.execute("""
        SELECT COUNT(*)                              AS ventas,
               SUM(Revenue)                          AS ingreso,
               SUM(Profit)                           AS beneficio,
               SUM(Profit) * 100.0 / SUM(Revenue)    AS margen,
               COUNT(DISTINCT SalesPersonID)         AS vendedores,
               MIN(SaleDate)                         AS desde,
               MAX(SaleDate)                         AS hasta
        FROM sales_data
    """).fetchone()
    kpis = {c: redondear(k[c]) for c in k.keys()}
    with open(os.path.join(salida, 'kpis.json'), 'w', encoding='utf-8') as f:
        json.dump(kpis, f, ensure_ascii=False, indent=1)
    print('  %-24s -> kpis.json' % 'kpis')

    # La quinta consulta filtra con HAVING AVG(Profit) < 1000 y con estos datos
    # no devuelve ni una fila. Un panel vacio no dice si es que no hay ningun
    # producto con margen bajo o si el informe esta roto, asi que se exporta
    # tambien el beneficio medio de TODAS las categorias: puestas al lado del
    # umbral se ve de un vistazo que ninguna se acerca, que es la conclusion.
    #
    # Va aqui y no en el .sql a proposito: el .sql es la entrega analitica del
    # proyecto y no se toca para adornar una demo.
    cats = [
        {kk: redondear(r[kk]) for kk in r.keys()}
        for r in con.execute("""
            SELECT ProductCategory,
                   AVG(Revenue) AS Avg_Revenue,
                   AVG(Cost)    AS Avg_Cost,
                   AVG(Profit)  AS Avg_Profit,
                   COUNT(*)     AS Ventas
            FROM sales_data
            GROUP BY ProductCategory
            ORDER BY Avg_Profit DESC
        """)
    ]
    with open(os.path.join(salida, 'categorias.json'), 'w', encoding='utf-8') as f:
        json.dump({'umbral': 1000, 'categorias': cats}, f, ensure_ascii=False, indent=1)
    print('  %-24s %2d filas -> categorias.json' % ('categorias (contexto)', len(cats)))
    print()
    print(json.dumps(kpis, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
