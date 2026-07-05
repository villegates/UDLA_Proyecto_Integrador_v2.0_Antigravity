import os
import tempfile
from pathlib import Path
import pandas as pd
from src.pipeline import generar_analisis_pagos


def test_generar_analisis_pagos_agrega_y_calcula_participacion():
    """
    Test 8: la capa de análisis une las 3 tablas y agrega por estado × método.
    Verifica que se generen los reportes analíticos y la base de datos de manera correcta.
    """
    # 1. Crear datos ficticios (Mock Data)
    df_pagos = pd.DataFrame({
        'order_id': ['o1', 'o2', 'o3'],
        'payment_value': [100.0, 200.0, 50.0],
        'payment_installments': [1, 2, 1],
        'payment_type': ['credit_card', 'credit_card', 'boleto'],
    })
    df_ordenes = pd.DataFrame({
        'order_id': ['o1', 'o2', 'o3'],
        'customer_id': ['c1', 'c2', 'c3'],
        'order_status': ['delivered', 'delivered', 'delivered'],
    })
    df_clientes = pd.DataFrame({
        'customer_id': ['c1', 'c2', 'c3'],
        'customer_state': ['SP', 'SP', 'SP'],
    })

    # 2. Configurar directorio temporal para evitar sobreescribir datos reales
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        
        # Estructura del config.yaml simulado
        config_mock = {
            "rutas": {
                "salida_reporte": "resumen_ejecutivo.csv",
                "salida_pagos": "pagos_por_metodo.csv",
                "salida_estados": "rendimiento_por_estado.csv",
                "salida_criticas": "ordenes_criticas.csv",
                "salida_explicacion_ia": "explicacion_patrones_ia.txt",
                "base_datos": "olist_analytics.db"
            }
        }
        
        # 3. Ejecutar la función de agregaciones analíticas
        resumen, df_comp, pagos_metodo, rend_estado, explicacion_ia = generar_analisis_pagos(
            df_pagos, df_ordenes, df_clientes, valor_dolar=180.0, config=config_mock, base_path=base_path
        )

        # 4. Aseveraciones (Asserts)
        # Comprobar que los archivos se crearon físicamente en el directorio temporal
        assert (base_path / "resumen_ejecutivo.csv").exists()
        assert (base_path / "pagos_por_metodo.csv").exists()
        assert (base_path / "olist_analytics.db").exists()

        # Verificar agregaciones del resumen por estado
        fila_sp = resumen[resumen['customer_state'] == 'SP'].iloc[0]
        assert fila_sp['transacciones'] == 3
        # total_ingresos_brl: 100 + 200 + 50 = 350
        assert fila_sp['total_ingresos_brl'] == 350.0

        # Verificar agregaciones por tipo de pago
        credit_card_data = pagos_metodo[pagos_metodo['payment_type'] == 'credit_card'].iloc[0]
        assert credit_card_data['cantidad_usos'] == 2
        assert credit_card_data['monto_total_brl'] == 300.0
