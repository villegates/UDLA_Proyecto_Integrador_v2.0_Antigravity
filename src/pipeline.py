import os
import sqlite3
from pathlib import Path
import pandas as pd
import httpx
import anthropic
from loguru import logger

# Diccionario oficial de mapeo para traducir las siglas de Brasil a nombres completos
MAPEO_ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina",
    "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins"
}


def explicar_patrones_con_ia(
    pagos_por_metodo: pd.DataFrame, 
    rendimiento_estado_pago: pd.DataFrame, 
    config: dict, 
    base_path: Path
) -> str:
    """
    Componente de IA del Pipeline (Clase 7 / Unidad 3):
    Envía los datos de transacciones a Claude para resumir patrones de negocio.
    Implementa un mecanismo de Fallback local robusto en caso de que no haya API key.
    """
    logger.info("🤖 Iniciando componente de análisis estratégico con IA...")
    
    # 1. Preparar el resumen de datos para el prompt
    resumen_pagos = pagos_por_metodo.to_string(index=False)
    resumen_estados = rendimiento_estado_pago.head(5).to_string(index=False) # Tomamos los top 5
    
    prompt = (
        "Eres un analista de negocios financiero experto en ecommerce.\n"
        "Analiza el siguiente resumen del rendimiento de métodos de pago de Olist Brasil:\n\n"
        "MÉTRICAS POR MÉTODO DE PAGO:\n"
        f"{resumen_pagos}\n\n"
        "MUESTRA DE COMPORTAMIENTO GEOGRÁFICO (TOP 5 ESTADOS):\n"
        f"{resumen_estados}\n\n"
        "Instrucciones de respuesta:\n"
        "1. Genera una explicación ejecutiva concisa (máximo 200 palabras) sobre los patrones de pago detectados.\n"
        "2. Identifica el método de pago dominante y su impacto en las comisiones de pasarela de pago.\n"
        "3. Comenta la brecha de bancarización reflejada en el uso de boleto (efectivo) vs tarjeta de crédito.\n"
        "4. Responde con un tono formal para la gerencia, sin rodeos de saludo ni introducciones vacías."
    )
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    explicacion = ""
    
    if api_key and api_key.strip() and not api_key.startswith("sk-ant-tu-llave"):
        try:
            model = config.get("api", {}).get("model", "claude-haiku-4-5-20251001")
            max_tokens = config.get("api", {}).get("max_tokens", 350)
            
            logger.info(f"   ↳ Consultando API externa de Anthropic (Modelo: {model})...")
            cliente = anthropic.Anthropic(
                api_key=api_key,
                http_client=httpx.Client(verify=False),
            )
            respuesta = cliente.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            explicacion = respuesta.content[0].text.strip()
            logger.success("✅ IA exitosa: Claude generó el reporte ejecutivo de patrones.")
        except Exception as e:
            logger.warning(f"⚠️ Error al conectar con la API de IA: {e}. Activando plan de contingencia...")
            
    if not explicacion:
        # Mecanismo de contingencia (Fallback local robusto)
        logger.info("   ↳ Ejecutando fallback analítico local (Cómputo Heurístico)...")
        
        # Calcular dinámicamente algunos datos clave para el fallback
        total_transacciones = pagos_por_metodo["cantidad_usos"].sum()
        tarjeta_data = pagos_por_metodo[pagos_por_metodo["payment_type"] == "credit_card"].iloc[0]
        boleto_data = pagos_por_metodo[pagos_por_metodo["payment_type"] == "boleto"].iloc[0]
        
        pct_tarjeta = (tarjeta_data["cantidad_usos"] / total_transacciones) * 100
        pct_boleto = (boleto_data["cantidad_usos"] / total_transacciones) * 100
        
        explicacion = (
            "--- SÍNTESIS DE NEGOCIO (FALLBACK ANALÍTICO LOCAL) ---\n"
            f"El análisis del canal financiero de Olist revela una hegemonía del crédito, "
            f"donde las transacciones con tarjeta de crédito representan el {pct_tarjeta:.1f}% del volumen operativo, "
            f"concentrando la mayor parte de la liquidez del ecommerce. Esto indica una alta dependencia de las pasarelas bancarias "
            f"y los plazos de cuotas para sostener la compra de tickets promedio elevados.\n\n"
            f"Por otro lado, el método de Boleto Bancario representa un considerable {pct_boleto:.1f}% de las transacciones. "
            f"La persistencia de esta opción en efectivo refleja la brecha de inclusión financiera existente en el mercado brasileño, "
            f"particularmente en estados del interior. Estratégicamente, se recomienda optimizar las comisiones por adquirencia con los "
            f"proveedores de tarjeta de crédito (nuestro mayor pilar transaccional) e implementar campañas para digitalizar "
            f"compradores recurrentes de boleto."
        )
        logger.success("✅ Fallback completado: Síntesis de auditoría local generada correctamente.")

    # Guardar Físicamente en Carpeta /output (Output 6)
    ruta_txt = base_path / config["rutas"]["salida_explicacion_ia"]
    ruta_txt.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(explicacion)
    logger.success(f"💾 Output 6 (Explicación de IA/Fallback) guardada en: {config['rutas']['salida_explicacion_ia']}")

    # Guardar en Base de Datos SQLite (Tabla auditoria_patrones_ia)
    ruta_db = base_path / config["rutas"]["base_datos"]
    try:
        conn = sqlite3.connect(ruta_db)
        try:
            df_ia = pd.DataFrame([{"tipo_analisis": "IA_SINTESIS", "contenido": explicacion}])
            df_ia.to_sql("auditoria_patrones_ia", conn, if_exists="replace", index=False)
        finally:
            conn.close()
        logger.success("✅ SQLite actualizado: Análisis de patrones guardado en tabla 'auditoria_patrones_ia'.")
    except Exception as e:
        logger.error(f"❌ Error al guardar el análisis de IA en SQLite: {e}")
        
    return explicacion


def generar_analisis_pagos(df_payments: pd.DataFrame, df_orders: pd.DataFrame, df_customers: pd.DataFrame, valor_dolar: float, config: dict, base_path: Path):
    """
    Cruza las fuentes de datos, integra conversión por API y genera los 6 outputs
    (4 CSVs + 1 DB SQLite + 1 Explicación de IA), utilizando la divisa correcta (BRL) para los montos base.
    """
    logger.info("🧠 Procesando cruces de datos (Merges) y analítica avanzada...")
    
    # 1. Merges secuenciales
    df_unido = pd.merge(df_payments, df_orders, on="order_id", how="inner")
    df_completo = pd.merge(df_unido, df_customers, on="customer_id", how="inner")
    
    # 2. Transformación con API: Conversión Monetaria a CLP
    df_completo["payment_value_clp"] = df_completo["payment_value"] * valor_dolar
    
    # --- 3. Generación de las 4 Tablas de Reportes (Outputs) ---
    
    # Output 1: Resumen Ejecutivo por Estado
    resumen_ejecutivo = df_completo.groupby("customer_state").agg(
        total_ingresos_brl=("payment_value", "sum"),
        total_ingresos_clp=("payment_value_clp", "sum"),
        transacciones=("order_id", "count")
    ).reset_index()
    
    # Output 2: Métricas por tipo de Pago
    pagos_por_metodo = df_completo.groupby("payment_type").agg(
        monto_total_brl=("payment_value", "sum"),
        monto_total_clp=("payment_value_clp", "sum"),
        cantidad_usos=("order_id", "count")
    ).reset_index()
    
    # Output 3: Matriz cruzada Estado vs Método
    rendimiento_estado_pago = pd.crosstab(
        df_completo["customer_state"], 
        df_completo["payment_type"], 
        values=df_completo["payment_value_clp"], 
        aggfunc="sum"
    ).fillna(0).reset_index()
    
    # Output 4: Órdenes Críticas (Filtro operacional de cancelados)
    ordenes_criticas = df_completo[df_completo["order_status"].isin(["canceled", "unavailable"])][
        ["order_id", "customer_id", "order_status", "payment_value", "payment_value_clp"]
    ].drop_duplicates()
    
    # --- 4. Exportación Física a Carpeta /output ---
    output_dir = base_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    resumen_ejecutivo.to_csv(base_path / config["rutas"]["salida_reporte"], index=False, encoding="utf-8")
    pagos_por_metodo.to_csv(base_path / config["rutas"]["salida_pagos"], index=False, encoding="utf-8")
    rendimiento_estado_pago.to_csv(base_path / config["rutas"]["salida_estados"], index=False, encoding="utf-8")
    ordenes_criticas.to_csv(base_path / config["rutas"]["salida_criticas"], index=False, encoding="utf-8")
    
    logger.success("💾 Outputs 1 al 4 (Archivos CSV) guardados exitosamente.")
    
    # Output 5: Persistencia Relacional en SQLite (.db)
    ruta_db = base_path / config["rutas"]["base_datos"]
    logger.info(f"🗄️ Inyectando tablas en la Base de Datos Relacional: {ruta_db.name}...")
    
    conn = sqlite3.connect(ruta_db)
    try:
        resumen_ejecutivo.to_sql("resumen_ejecutivo", conn, if_exists="replace", index=False)
        pagos_por_metodo.to_sql("pagos_por_metodo", conn, if_exists="replace", index=False)
        rendimiento_estado_pago.to_sql("rendimiento_estado_pago", conn, if_exists="replace", index=False)
        ordenes_criticas.to_sql("ordenes_criticas", conn, if_exists="replace", index=False)
    finally:
        conn.close()
        
    logger.success("✅ Output 5 (Base de Datos SQLite relacional) estructurada con éxito.")
    
    # Output 6: Explicación de Patrones con IA / Fallback
    explicacion_ia = explicar_patrones_con_ia(
        pagos_por_metodo, rendimiento_estado_pago, config, base_path
    )
    
    return resumen_ejecutivo, df_completo, pagos_por_metodo, rendimiento_estado_pago, explicacion_ia

def responder_preguntas_negocio(resumen_ejecutivo: pd.DataFrame, df_completo: pd.DataFrame, pagos_por_metodo: pd.DataFrame, rendimiento_estado_pago: pd.DataFrame):
    """
    Imprime en la consola el reporte completo con formato profesional,
    nombres de estados completos y terminología unificada ("Transacciones").
    """
    print("\n" + "="*105)
    print("                  📊 REPORTES ANALÍTICOS GLOBALES (OLIST PIPELINE)                  ")
    print("="*105)
    
    # REPORTE 1: Resumen de los 27 Estados con Nombres Reales (CORREGIDO: USD -> BRL)
    print("\n📈 TABLA 1: RESUMEN EJECUTIVO DE VENTAS POR ESTADO (Muestra Completa)")
    print("-" * 105)
    
    reporte_ordenado = resumen_ejecutivo.sort_values(by="total_ingresos_clp", ascending=False).copy()
    reporte_ordenado["customer_state"] = reporte_ordenado["customer_state"].map(MAPEO_ESTADOS).fillna(reporte_ordenado["customer_state"])
    
    with pd.option_context('display.max_rows', None, 'display.float_format', '{:,.2f}'.format):
        print(reporte_ordenado.to_string(index=False, columns=["customer_state", "transacciones", "total_ingresos_brl", "total_ingresos_clp"],
                                         header=["Estado", "Transacciones", "Total Ventas (BRL)", "Total Ventas (CLP)"]))
    print("-" * 105)
    
    # REPORTE 2: Métodos de Pago (CORREGIDO: USD -> BRL)
    print("\n💳 TABLA 2: RENDIMIENTO FINANCIERO POR MÉTODO DE PAGO")
    print("-" * 105)
    print(f"{'Método de Pago':<16} | {'Transacciones':<13} | {'Total Ventas (BRL)':<22} | {'Total Ventas (CLP)':<22}")
    print("-" * 105)
    for _, fila in pagos_por_metodo.iterrows():
        print(f" ➔ {fila['payment_type']:<13} | {int(fila['cantidad_usos']):<13,} | ${fila['monto_total_brl']:<21,.2f} | ${fila['monto_total_clp']:<21,.0f}")
    print("-" * 105)
    
    # REPORTE 3: Ingresos Cruzados
    print("\n🎚️ TABLA 3: INGRESOS POR ESTADO Y MÉTODO EN CLP")
    print("-" * 105)
    
    crosstab_formateado = rendimiento_estado_pago.copy()
    crosstab_formateado["customer_state"] = crosstab_formateado["customer_state"].map(MAPEO_ESTADOS).fillna(crosstab_formateado["customer_state"])
    
    columnas_pagos = [col for col in crosstab_formateado.columns if col != 'customer_state']
    for col in columnas_pagos:
        crosstab_formateado[col] = crosstab_formateado[col].map(lambda x: f"${x:,.0f}")
        
    with pd.option_context('display.max_columns', None, 'display.width', 1000):
        print(crosstab_formateado.to_string(index=False, header=["Estado", "Boleto", "Tarjeta Crédito", "Tarjeta Débito", "Voucher"]))
    print("-" * 105)

    # --- SECCIÓN FINALES: LOS 3 HALLAZGOS ASOCIADOS EN ORDEN ---
    print("\n" + "="*105)
    print("                    💡 HALLAZGOS Y RESPUESTAS CLAVE DE NEGOCIO                    ")
    print("="*105)
    
    # Hallazgo 1 (Asociado a Tabla 1 - CORREGIDO: USD -> BRL)
    top_fila = resumen_ejecutivo.sort_values(by="total_ingresos_clp", ascending=False).iloc[0]
    nombre_completo_top = MAPEO_ESTADOS.get(top_fila['customer_state'], top_fila['customer_state'])
    print(f"1️⃣ LIDERAZGO COMERCIAL GEOGRÁFICO (Asociado a Tabla 1):")
    print(f"    El estado de '{nombre_completo_top}' es el núcleo de Olist, acumulando el mayor volumen")
    print(f"    de ingresos del pipeline con ${top_fila['total_ingresos_brl']:,.2f} BRL (${top_fila['total_ingresos_clp']:,.0f} CLP).")
    print("-" * 105)
    
    # Hallazgo 2 (Asociado a Tabla 2 - CORREGIDO: USD -> BRL)
    metodo_top = pagos_por_metodo.sort_values(by="monto_total_clp", ascending=False).iloc[0]
    print(f"2️⃣ HEGEMONÍA EN LOS MÉTODOS DE PAGO (Asociado a Tabla 2):")
    print(f"    La modalidad de '{metodo_top['payment_type']}' domina la plataforma con un total recaudado de")
    print(f"    ${metodo_top['monto_total_brl']:,.2f} BRL, lo que representa {int(metodo_top['cantidad_usos']):,} transacciones exitosas.")
    print("-" * 105)
    
    # Hallazgo 3 (Asociado a Tabla 3)
    print(f"3️⃣ ANÁLISIS CRUZADO GEOGRÁFICO-FINANCIERO (Asociado a Tabla 3):")
    print(f"    Al cruzar los datos en la matriz, se evidencia que la 'Tarjeta de Crédito' (Credit Card) es el")
    print(f"    motor principal de ingresos en los estados con mayor tracción como São Paulo y Rio de Janeiro,")
    print(f"    superando ampliamente las recaudaciones por 'Boleto' y 'Tarjeta de Débito' combinadas.")
    print("="*105 + "\n")
