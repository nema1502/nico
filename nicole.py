import streamlit as st
import pandas as pd
import altair as alt

def obtener_monto():
    return st.number_input("Ingrese el monto para el cual quiere realizar el plan de gastos mensual en bolivianos (Bs): ", min_value=0.0, step=0.01)

def obtener_porcentaje_ahorro():
    return st.selectbox("¿Cuánto quiere ahorrar? (0%, 3%, 6%, 9%):", [0, 3, 6, 9]) / 100

def obtener_gasto_si_no(mensaje):
    if st.checkbox(mensaje):
        return st.number_input(f"¿Cuánto paga por {mensaje.lower()}?", min_value=0.0, step=0.01)
    else:
        return 0

def seleccionar_categorias():
    categorias = ["ALIMENTACION", "SERVICIOS BASICOS", "TRANSPORTE", "OCIO", "COMUNICACION", "SALUD"]
    seleccionadas = []
    for categoria in categorias:
        if st.checkbox(f"¿Tiene gasto en la categoría {categoria}?"):
            seleccionadas.append(categoria)
    return seleccionadas

def prioridad_categorias(seleccionadas):
    prioridades = {}
    for categoria in seleccionadas:
        prioridad = st.selectbox(f"Asignar prioridad a {categoria} (1 para la más importante, {len(seleccionadas)} para la menos importante):", list(range(1, len(seleccionadas) + 1)))
        prioridades[categoria] = prioridad
    return prioridades

def calcular_porcentajes(prioridades):
    n = len(prioridades)
    porcentaje_categoria = {
        1: {1: 100},
        2: {1: 60, 2: 40},
        3: {1: 45, 2: 30, 3: 25},
        4: {1: 32, 2: 27, 3: 23, 4: 18},
        5: {1: 30, 2: 25, 3: 20, 4: 15, 5: 10},
        6: {1: 26, 2: 22, 3: 19, 4: 15, 5: 11, 6: 7}
    }
    return {categoria: porcentaje_categoria[n][prioridad] / 100 for categoria, prioridad in prioridades.items()}

def calcular_subcategorias(categoria):
    subcategorias = []
    if categoria == "SERVICIOS BASICOS":
        subcategorias = ["LUZ", "AGUA", "GAS"]
    elif categoria == "COMUNICACION":
        subcategorias = ["CREDITO", "INTERNET"]
    
    prioridades = {}
    for subcategoria in subcategorias:
        prioridad = st.selectbox(f"Asignar prioridad a {subcategoria} (1 para la más importante, {len(subcategorias)} para la menos importante):", list(range(1, len(subcategorias) + 1)))
        prioridades[subcategoria] = prioridad

    n = len(prioridades)
    porcentaje_subcategoria = {
        1: {1: 100},
        2: {1: 60, 2: 40},
        3: {1: 45, 2: 30, 3: 25}
    }
    return {subcategoria: porcentaje_subcategoria[n][prioridad] / 100 for subcategoria, prioridad in prioridades.items()}

def main():
    st.title("Plan de Gastos Mensual")

    monto = obtener_monto()
    porcentaje_ahorro = obtener_porcentaje_ahorro()
    ahorro = monto * porcentaje_ahorro

    alquiler = obtener_gasto_si_no("¿Paga alquiler?")
    deudas = obtener_gasto_si_no("¿Tiene deudas económicas o educativas?")
    actividades = obtener_gasto_si_no("¿Realiza actividades extracurriculares?")

    total_1 = monto - alquiler - deudas - actividades
    total_2 = total_1 * porcentaje_ahorro
    total_final = total_1 - total_2

    seleccionadas = seleccionar_categorias()
    prioridades = prioridad_categorias(seleccionadas)
    porcentajes = calcular_porcentajes(prioridades)

    resultados = {}
    for categoria, porcentaje in porcentajes.items():
        if categoria in ["SERVICIOS BASICOS", "COMUNICACION"]:
            subcategorias = calcular_subcategorias(categoria)
            resultados[categoria] = {subcategoria: total_final * porcentaje * porcentaje_subcategoria for subcategoria, porcentaje_subcategoria in subcategorias.items()}
        else:
            resultados[categoria] = total_final * porcentaje

    resultados["AHORRO"] = ahorro
    resultados["ALQUILER"] = alquiler
    resultados["ACTIVIDADES EXTRACURRICULARES"] = actividades
    resultados["DEUDAS"] = deudas

    total_gastos_fijos = alquiler + deudas + actividades + ahorro
    total_gastos_variable = sum([sum(v.values()) if isinstance(v, dict) else v for k, v in resultados.items() if k not in ["AHORRO", "ALQUILER", "ACTIVIDADES EXTRACURRICULARES", "DEUDAS"]])
    total_gastos = total_gastos_fijos + total_gastos_variable
    sobrante = monto - total_gastos

    st.write("## Este sería tu plan de gastos mensual:")
    for categoria, valor in resultados.items():
        if isinstance(valor, dict):
            st.write(f"### {categoria}:")
            for subcategoria, subvalor in valor.items():
                st.write(f"{subcategoria}: {subvalor:.2f} Bs")
        else:
            st.write(f"{categoria}: {valor:.2f} Bs")

    st.write("## Resumen:")
    st.write(f"**Total Gastos Fijos:** {total_gastos_fijos:.2f} Bs")
    st.write(f"**Total Gastos Variables:** {total_gastos_variable:.2f} Bs")
    st.write(f"**Total Gastos:** {total_gastos:.2f} Bs")
    st.write(f"**Dinero Sobrante para Otros Gastos:** {sobrante:.2f} Bs")

    # Crear un gráfico de distribución de gastos
    categorias = list(resultados.keys())
    valores = [sum(v.values()) if isinstance(v, dict) else v for v in resultados.values()]

    df = pd.DataFrame({
        'Categoria': categorias,
        'Monto (Bs)': valores
    })

    chart = alt.Chart(df).mark_bar().encode(
        x='Monto (Bs)',
        y=alt.Y('Categoria', sort='-x')
    ).properties(
        title='Distribución de Gastos Mensuales'
    )

    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
