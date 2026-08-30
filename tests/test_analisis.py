"""
Pruebas del analisis de ventas en SQL.

Aqui lo que se publica no es codigo: son cinco consultas y los numeros que
salen de ellas. Estas pruebas protegen tres cosas distintas, y conviene no
confundirlas:

  1. Que el CSV es internamente coherente. Si Profit deja de ser
     Revenue - Cost, las cinco consultas siguen ejecutandose sin un solo
     error y publican un margen falso.
  2. Que el troceador del .sql devuelve exactamente las cinco consultas.
     Ya fallo una vez: la ultima termina en "< 1000; -- Asumiendo que...",
     y ese comentario de detras del punto y coma se convertia en una sexta
     consulta fantasma.
  3. Que el margen de la cabecera se calcula sobre los totales y no como
     promedio de los margenes por region -- el error de promediar promedios,
     que da un numero distinto y de aspecto igual de creible.
"""

import csv
import json
import os
import sqlite3
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import export_results as exp

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- Material de trabajo --------------------------------------------------


@pytest.fixture(scope="module")
def filas_csv():
    with open(exp.CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture()
def con(filas_csv):
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    exp.cargar(c)
    yield c
    c.close()


# --- El dato de partida ---------------------------------------------------


class TestCoherenciaDelCSV:
    def test_tiene_las_columnas_que_piden_las_consultas(self, filas_csv):
        esperadas = {
            "SaleID",
            "SaleDate",
            "Region",
            "ProductCategory",
            "Revenue",
            "Cost",
            "SalesPersonID",
            "CustomerType",
            "Profit",
        }
        assert esperadas <= set(filas_csv[0].keys())

    def test_no_esta_vacio(self, filas_csv):
        assert len(filas_csv) > 100

    def test_el_beneficio_es_el_ingreso_menos_el_coste_en_todas_las_filas(
        self, filas_csv
    ):
        """
        Si esta identidad se rompe, ninguna consulta protesta: todas siguen
        ejecutandose y publican un margen que no se sostiene.
        """
        descuadres = [
            r["SaleID"]
            for r in filas_csv
            if abs((float(r["Revenue"]) - float(r["Cost"])) - float(r["Profit"])) > 0.01
        ]
        assert not descuadres, f"{len(descuadres)} ventas descuadradas: {descuadres[:5]}"

    def test_los_importes_son_numeros(self, filas_csv):
        for r in filas_csv[:200]:
            for columna in ("Revenue", "Cost", "Profit"):
                float(r[columna])

    def test_el_ingreso_nunca_es_negativo(self, filas_csv):
        assert not [r["SaleID"] for r in filas_csv if float(r["Revenue"]) < 0]

    def test_las_fechas_tienen_el_formato_que_espera_strftime(self, filas_csv):
        """La consulta 4 agrupa con strftime('%Y-%m'): un formato distinto no
        da error, agrupa mal y en silencio."""
        for r in filas_csv[:200]:
            fecha = r["SaleDate"]
            assert len(fecha) == 10 and fecha[4] == "-" and fecha[7] == "-", fecha

    def test_ningun_identificador_de_venta_esta_repetido(self, filas_csv):
        ids = [r["SaleID"] for r in filas_csv]
        assert len(ids) == len(set(ids))


# --- La carga en SQLite ---------------------------------------------------


class TestCarga:
    def test_mete_todas_las_filas(self, filas_csv):
        c = sqlite3.connect(":memory:")
        assert exp.cargar(c) == len(filas_csv)
        assert c.execute("SELECT COUNT(*) FROM sales_data").fetchone()[0] == len(
            filas_csv
        )

    def test_los_importes_entran_como_numeros_y_no_como_texto(self, con):
        fila = con.execute("SELECT Revenue, Cost, Profit, Region FROM sales_data").fetchone()
        assert isinstance(fila["Revenue"], float)
        assert isinstance(fila["Cost"], float)
        assert isinstance(fila["Profit"], float)
        assert isinstance(fila["Region"], str)

    def test_se_pueden_sumar_de_verdad(self, con, filas_csv):
        """Con Revenue como TEXT, SUM() devolveria 0 sin quejarse."""
        total = con.execute("SELECT SUM(Revenue) FROM sales_data").fetchone()[0]
        assert total == pytest.approx(sum(float(r["Revenue"]) for r in filas_csv), rel=1e-9)


# --- El troceador del .sql ------------------------------------------------


class TestConsultas:
    def test_devuelve_exactamente_las_cinco_del_fichero(self):
        assert len(exp.consultas()) == len(exp.NOMBRES) == 5

    def test_ninguna_consulta_conserva_comentarios(self):
        for q in exp.consultas():
            assert "--" not in q

    def test_todas_empiezan_por_select(self):
        for q in exp.consultas():
            assert q.lstrip().upper().startswith("SELECT")

    def test_un_comentario_detras_del_ultimo_punto_y_coma_no_es_una_consulta(
        self, tmp_path, monkeypatch
    ):
        """El fallo original: la sexta consulta fantasma."""
        falso = tmp_path / "x.sql"
        falso.write_text(
            "-- cabecera\nSELECT 1;\nSELECT 2; -- Asumiendo que esto es bajo\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(exp, "SQL", str(falso))
        assert exp.consultas() == ["SELECT 1", "SELECT 2"]

    def test_las_cinco_se_ejecutan_sobre_los_datos_reales(self, con):
        for nombre, q in zip(exp.NOMBRES, exp.consultas()):
            con.execute(q).fetchall()  # no debe lanzar

    def test_el_ranking_de_vendedores_devuelve_cinco_como_mucho(self, con):
        q = exp.consultas()[1]
        assert len(con.execute(q).fetchall()) <= 5

    def test_el_ranking_de_vendedores_viene_ordenado_de_mayor_a_menor(self, con):
        ingresos = [r["Total_Revenue"] for r in con.execute(exp.consultas()[1])]
        assert ingresos == sorted(ingresos, reverse=True)

    def test_las_regiones_suman_el_ingreso_total(self, con):
        """Un GROUP BY que se deje filas fuera no da error: da un total menor."""
        por_region = sum(r["Total_Revenue"] for r in con.execute(exp.consultas()[0]))
        total = con.execute("SELECT SUM(Revenue) FROM sales_data").fetchone()[0]
        assert por_region == pytest.approx(total, rel=1e-9)

    def test_la_tendencia_mensual_sale_en_orden_cronologico(self, con):
        meses = [r["Sales_Month"] for r in con.execute(exp.consultas()[3])]
        assert meses == sorted(meses)
        assert len(meses) == len(set(meses))

    def test_cada_mes_tiene_la_forma_aaaa_mm(self, con):
        for r in con.execute(exp.consultas()[3]):
            mes = r["Sales_Month"]
            assert len(mes) == 7 and mes[4] == "-", mes

    def test_el_umbral_de_margen_bajo_es_el_que_documenta_la_consulta(self, con):
        """
        La quinta consulta filtra con HAVING AVG(Profit) < 1000. Si devuelve
        filas, todas tienen que estar por debajo del umbral; si no devuelve
        ninguna, ninguna categoria puede estarlo.
        """
        bajas = list(con.execute(exp.consultas()[4]))
        for r in bajas:
            assert r["Avg_Profit"] < 1000
        todas = list(
            con.execute(
                "SELECT ProductCategory, AVG(Profit) AS m FROM sales_data GROUP BY ProductCategory"
            )
        )
        esperadas = {r["ProductCategory"] for r in todas if r["m"] < 1000}
        assert {r["ProductCategory"] for r in bajas} == esperadas


# --- Lo que acaba publicado ----------------------------------------------


class TestExportacion:
    @pytest.fixture(scope="class")
    def salida(self, tmp_path_factory):
        destino = tmp_path_factory.mktemp("resultados")
        proceso = subprocess.run(
            [sys.executable, os.path.join(AQUI, "export_results.py"), str(destino)],
            capture_output=True,
            text=True,
        )
        assert proceso.returncode == 0, proceso.stderr
        return destino

    def leer(self, salida, nombre):
        with open(os.path.join(str(salida), nombre), encoding="utf-8") as f:
            return json.load(f)

    @pytest.mark.parametrize(
        "fichero",
        [
            "regiones.json",
            "top_vendedores.json",
            "clientes_por_categoria.json",
            "tendencia_mensual.json",
            "margen_bajo.json",
            "kpis.json",
            "categorias.json",
        ],
    )
    def test_escribe_todos_los_ficheros_que_consume_el_panel(self, salida, fichero):
        assert os.path.exists(os.path.join(str(salida), fichero))

    def test_el_margen_de_la_cabecera_sale_de_los_totales(self, salida, filas_csv):
        """
        No es el promedio de los margenes por region: promediar promedios da
        otro numero, igual de creible y equivocado.
        """
        kpis = self.leer(salida, "kpis.json")
        ingreso = sum(float(r["Revenue"]) for r in filas_csv)
        beneficio = sum(float(r["Profit"]) for r in filas_csv)
        assert kpis["margen"] == pytest.approx(beneficio * 100.0 / ingreso, abs=0.01)

    def test_la_cabecera_cuadra_con_el_csv(self, salida, filas_csv):
        kpis = self.leer(salida, "kpis.json")
        assert kpis["ventas"] == len(filas_csv)
        assert kpis["ingreso"] == pytest.approx(
            sum(float(r["Revenue"]) for r in filas_csv), abs=0.5
        )
        assert kpis["vendedores"] == len({r["SalesPersonID"] for r in filas_csv})

    def test_el_periodo_de_la_cabecera_es_el_que_cubre_el_csv(self, salida, filas_csv):
        kpis = self.leer(salida, "kpis.json")
        fechas = [r["SaleDate"] for r in filas_csv]
        assert kpis["desde"] == min(fechas)
        assert kpis["hasta"] == max(fechas)

    def test_las_regiones_publicadas_suman_el_ingreso_de_la_cabecera(self, salida):
        kpis = self.leer(salida, "kpis.json")
        regiones = self.leer(salida, "regiones.json")
        assert sum(r["Total_Revenue"] for r in regiones) == pytest.approx(
            kpis["ingreso"], abs=1.0
        )

    def test_publica_el_contexto_de_categorias_aunque_no_haya_margen_bajo(self, salida):
        """
        margen_bajo.json sale vacio con estos datos. Un panel vacio no distingue
        entre "no hay ninguna categoria con margen bajo" y "el informe esta
        roto", asi que se publica tambien el beneficio medio de todas las
        categorias junto al umbral.
        """
        contexto = self.leer(salida, "categorias.json")
        assert contexto["umbral"] == 1000
        assert len(contexto["categorias"]) >= 1
        for c in contexto["categorias"]:
            assert {"ProductCategory", "Avg_Profit", "Ventas"} <= set(c)

    def test_las_categorias_del_contexto_suman_todas_las_ventas(self, salida, filas_csv):
        contexto = self.leer(salida, "categorias.json")
        assert sum(c["Ventas"] for c in contexto["categorias"]) == len(filas_csv)

    def test_el_contexto_viene_ordenado_por_beneficio_medio(self, salida):
        medios = [c["Avg_Profit"] for c in self.leer(salida, "categorias.json")["categorias"]]
        assert medios == sorted(medios, reverse=True)

    def test_los_json_no_llevan_secuencias_de_escape_en_los_acentos(self, salida):
        crudo = open(os.path.join(str(salida), "regiones.json"), encoding="utf-8").read()
        assert "\\u00" not in crudo
