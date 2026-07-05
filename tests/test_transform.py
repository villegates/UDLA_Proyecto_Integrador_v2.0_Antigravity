import pytest
import pandas as pd
from src.transform import (
    limpiar_y_validar_datos,
    validar_contrato_pagos,
    validar_contrato_ordenes,
    validar_contrato_clientes,
)


def test_aislamiento_datos_sucios():
    """
    Prueba unitaria para verificar que la capa de transformación aísla
    correctamente las filas corruptas (valores de pago <= 0 o cuotas < 1).
    """
    # 1. Creamos datos de prueba ficticios (Mock Data)
    df_pagos_mock = pd.DataFrame({
        'order_id': ['orden_1', 'orden_2', 'orden_3'],
        'payment_value': [150.0, -10.0, 200.0],          # El -10.0 es corrupto
        'payment_installments': [3, 1, 0],               # El 0 es corrupto
        'payment_type': ['credit_card', 'boleto', 'voucher']  # Columna requerida por el contrato
    })
    
    df_ordenes_mock = pd.DataFrame({
        'order_id': ['orden_1', 'orden_2', 'orden_3'],
        'customer_id': ['cliente_1', 'cliente_2', 'cliente_3'], # Columna agregada para cumplir el contrato
        'order_status': ['delivered', 'delivered', 'delivered']
    })

    df_clientes_mock = pd.DataFrame({
        'customer_id': ['cliente_1', 'cliente_2', 'cliente_3'],
        'customer_state': ['SP', 'RJ', 'AM']
    })

    # 2. Ejecutamos la función de transformación
    df_p_limpio, _, _ = limpiar_y_validar_datos(df_pagos_mock, df_ordenes_mock, df_clientes_mock)

    # 3. Aseveraciones (Asserts)
    # De las 3 filas, solo la 'orden_1' cumple simultáneamente el contrato (valor > 0 y cuotas >= 1)
    assert len(df_p_limpio) == 1, f"Se esperaba 1 fila limpia, pero quedaron {len(df_p_limpio)}"
    assert df_p_limpio.iloc[0]['order_id'] == 'orden_1'


def test_filtrado_ordenes_canceladas():
    """
    Prueba unitaria para verificar que el pipeline excluye del análisis
    las órdenes con estado 'canceled' para no inflar métricas.
    """
    df_pagos_mock = pd.DataFrame({
        'order_id': ['orden_1', 'orden_2', 'orden_3'],
        'payment_value': [100.0, 200.0, 300.0],
        'payment_installments': [1, 2, 1],
        'payment_type': ['credit_card', 'credit_card', 'boleto']
    })
    
    df_ordenes_mock = pd.DataFrame({
        'order_id': ['orden_1', 'orden_2', 'orden_3'],
        'customer_id': ['cliente_1', 'cliente_2', 'cliente_3'], # Columna agregada para cumplir el contrato
        'order_status': ['delivered', 'canceled', 'unavailable'] # Se verifica el comportamiento de filtrado
    })

    df_clientes_mock = pd.DataFrame({
        'customer_id': ['cliente_1', 'cliente_2', 'cliente_3'],
        'customer_state': ['SP', 'RJ', 'AM']
    })

    _, df_o_limpio, _ = limpiar_y_validar_datos(df_pagos_mock, df_ordenes_mock, df_clientes_mock)

    # El pipeline remueve 'canceled' pero mantiene 'unavailable', por lo que quedan 2 órdenes
    estados_restantes = set(df_o_limpio['order_status'].unique())
    assert len(df_o_limpio) == 2
    assert 'canceled' not in estados_restantes
    assert 'unavailable' in estados_restantes


def test_comportamiento_tipos_y_columnas():
    """
    Prueba unitaria para verificar que los tipos de datos de las columnas clave
    y las estructuras esenciales se mantengan correctas post-transformación.
    """
    df_pagos_mock = pd.DataFrame({
        'order_id': ['orden_1'],
        'payment_value': [50.0],
        'payment_installments': [1],
        'payment_type': ['boleto']
    })
    
    df_ordenes_mock = pd.DataFrame({
        'order_id': ['orden_1'],
        'customer_id': ['cliente_1'], # Columna agregada para cumplir el contrato
        'order_status': ['delivered']
    })

    df_clientes_mock = pd.DataFrame({
        'customer_id': ['cliente_1'],
        'customer_state': ['SP']
    })

    df_p_limpio, df_o_limpio, df_c_limpio = limpiar_y_validar_datos(df_pagos_mock, df_ordenes_mock, df_clientes_mock)

    # Validamos tipos de datos requeridos para evitar fallos de agregación en Pandas
    assert pd.api.types.is_numeric_dtype(df_p_limpio['payment_value'])
    assert pd.api.types.is_numeric_dtype(df_p_limpio['payment_installments'])
    
    # Comprobar la integridad de las columnas del contrato de pagos
    columnas_pagos = set(df_p_limpio.columns)
    for col in ['order_id', 'payment_value', 'payment_installments', 'payment_type']:
        assert col in columnas_pagos, f"La columna esencial '{col}' se perdió en la transformación"

    # Comprobar la integridad de las columnas del contrato de órdenes
    columnas_ordenes = set(df_o_limpio.columns)
    for col in ['order_id', 'customer_id', 'order_status']:
        assert col in columnas_ordenes, f"La columna esencial de órdenes '{col}' se perdió"

    # Comprobar la integridad de las columnas del contrato de clientes
    columnas_clientes = set(df_c_limpio.columns)
    for col in ['customer_id', 'customer_state']:
        assert col in columnas_clientes, f"La columna esencial de clientes '{col}' se perdió"


def test_contratos_rechazan_datos_invalidos():
    """
    Test 4 (negativo): los contratos de calidad deben LANZAR AssertionError
    ante datos que violan las reglas. Verifica que la validación realmente protege.
    """
    # Pagos con monto negativo → viola la Regla 3 del contrato de pagos
    pagos_malos = pd.DataFrame({
        'order_id': ['orden_1'],
        'payment_value': [-50.0],
        'payment_installments': [1],
        'payment_type': ['credit_card'],
    })
    with pytest.raises(AssertionError):
        validar_contrato_pagos(pagos_malos)

    # Órdenes con order_id duplicado → viola la Regla 2 (llave primaria única)
    ordenes_malas = pd.DataFrame({
        'order_id': ['orden_1', 'orden_1'],
        'customer_id': ['cl_1', 'cl_2'],
        'order_status': ['delivered', 'delivered'],
    })
    with pytest.raises(AssertionError):
        validar_contrato_ordenes(ordenes_malas)


def test_contrato_clientes_valido():
    """
    Test 5 (positivo): Verifica que un dataset de clientes bien estructurado
    y con estados válidos pase el contrato formal.
    """
    clientes_buenos = pd.DataFrame({
        'customer_id': ['c1', 'c2', 'c3'],
        'customer_state': ['SP', 'RJ', 'AM']
    })
    validar_contrato_clientes(clientes_buenos)


def test_contrato_clientes_invalidos():
    """
    Test 6 (negativo): Verifica que el contrato de clientes falle ante estados inexistentes,
    IDs duplicados o columnas faltantes.
    """
    # Estado geográfico inválido (XX)
    clientes_malos_estado = pd.DataFrame({
        'customer_id': ['c1'],
        'customer_state': ['XX']
    })
    with pytest.raises(AssertionError):
        validar_contrato_clientes(clientes_malos_estado)

    # ID de cliente duplicado
    clientes_malos_duplicados = pd.DataFrame({
        'customer_id': ['c1', 'c1'],
        'customer_state': ['SP', 'RJ']
    })
    with pytest.raises(AssertionError):
        validar_contrato_clientes(clientes_malos_duplicados)

    # Columnas faltantes
    clientes_malos_columnas = pd.DataFrame({
        'customer_id': ['c1']
    })
    with pytest.raises(AssertionError):
        validar_contrato_clientes(clientes_malos_columnas)


def test_contratos_rechazan_nulos():
    """
    Test 7 (negativo): Verifica que todos los contratos fallen si hay valores nulos en
    sus respectivas columnas primarias o críticas de negocio.
    """
    # Nulo en pagos
    pagos_nulos = pd.DataFrame({
        'order_id': [None],
        'payment_value': [100.0],
        'payment_installments': [1],
        'payment_type': ['credit_card']
    })
    with pytest.raises(AssertionError):
        validar_contrato_pagos(pagos_nulos)

    # Nulo en órdenes
    ordenes_nulas = pd.DataFrame({
        'order_id': ['orden_1'],
        'customer_id': [None],
        'order_status': ['delivered']
    })
    with pytest.raises(AssertionError):
        validar_contrato_ordenes(ordenes_nulas)

    # Nulo en clientes
    clientes_nulos = pd.DataFrame({
        'customer_id': ['c1'],
        'customer_state': [None]
    })
    with pytest.raises(AssertionError):
        validar_contrato_clientes(clientes_nulos)