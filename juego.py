import streamlit as st
import random

# ─────────────────────────────────────────────
# CONFIGURACIÓN BASE
# ─────────────────────────────────────────────
COLORES = ["Rojo", "Verde", "Blanco", "Naranja", "Amarillo", "Azul"]
COLOR_HEX = {
    "Rojo": "#e74c3c", "Verde": "#27ae60", "Blanco": "#bdc3c7",
    "Naranja": "#e67e22", "Amarillo": "#f1c40f", "Azul": "#2980b9"
}
AFINIDADES = {
    "Rojo":    ["Blanco", "Verde"],
    "Verde":   ["Blanco", "Rojo", "Naranja"],
    "Blanco":  ["Naranja", "Verde", "Rojo", "Amarillo"],
    "Naranja": ["Blanco", "Amarillo", "Azul", "Verde"],
    "Amarillo":["Naranja", "Blanco", "Azul"],
    "Azul":    ["Naranja", "Amarillo"]
}
PESOS_AFINIDAD = [80, 60, 40, 20]
NUM_DISTRITOS = 150
NUM_PROVINCIAS = 30
DISTRITOS_POR_PROVINCIA = 5
UMBRAL_CANDIDATURA = 0.15
POBLACION_DISTRITO = 100_000
POBLACION_PROVINCIA = 500_000
POBLACION_TOTAL = 15_000_000

# ─────────────────────────────────────────────
# BLOQUE 1 — DISTRIBUCIÓN IDEOLÓGICA
# ─────────────────────────────────────────────
def distribuir_ideologia():
    """Distribuye la población por color en cada distrito. Mínimo 5% por color."""
    distritos = []
    for d in range(1, NUM_DISTRITOS + 1):
        while True:
            cortes = sorted(random.sample(range(1, 100), 5))
            partes = [cortes[0]] + [cortes[i]-cortes[i-1] for i in range(1,5)] + [100-cortes[4]]
            if all(p >= 5 for p in partes):
                dist = {COLORES[i]: partes[i] / 100 for i in range(6)}
                distritos.append({"numero": d, "poblacion": dist})
                break
    return distritos

def calcular_provincias(distritos):
    """Agrupa distritos en provincias (5 distritos por provincia)."""
    provincias = []
    for p in range(NUM_PROVINCIAS):
        inicio = p * DISTRITOS_POR_PROVINCIA
        grupo = distritos[inicio:inicio + DISTRITOS_POR_PROVINCIA]
        pob_prov = {}
        for color in COLORES:
            pob_prov[color] = sum(d["poblacion"][color] for d in grupo) / DISTRITOS_POR_PROVINCIA
        provincias.append({"numero": p + 1, "distritos": grupo, "poblacion": pob_prov})
    return provincias

def calcular_pais(provincias):
    """Calcula la distribución ideológica nacional."""
    pob_pais = {}
    for color in COLORES:
        pob_pais[color] = sum(p["poblacion"][color] for p in provincias) / NUM_PROVINCIAS
    return pob_pais

# ─────────────────────────────────────────────
# BLOQUE 2 — SISTEMA DE VOTOS CON AFINIDADES
# ─────────────────────────────────────────────
def calcular_votos(poblacion, candidatos):
    """
    Dado un dict de población por color y una lista de colores con candidato,
    devuelve los votos finales por candidato (normalizados).
    """
    votos = {c: 0.0 for c in candidatos}
    nulos = 0.0

    for color, porcentaje in poblacion.items():
        if color in candidatos:
            votos[color] += porcentaje
        else:
            # Sin candidato: 15% nulo, 85% redistribuido por afinidades
            nulos += porcentaje * 0.15
            redistribuible = porcentaje * 0.85

            # Filtrar afinidades que tienen candidato
            afs = [a for a in AFINIDADES[color] if a in candidatos]

            if not afs:
                nulos += redistribuible
            else:
                pesos = PESOS_AFINIDAD[:len(afs)]
                total_pesos = sum(pesos)
                for i, af in enumerate(afs):
                    votos[af] += redistribuible * (pesos[i] / total_pesos)

    return votos, nulos

def obtener_candidatos(poblacion):
    """Devuelve los colores que superan el umbral del 15%."""
    return [c for c, p in poblacion.items() if p >= UMBRAL_CANDIDATURA]

# ─────────────────────────────────────────────
# BLOQUE 3 — ELECCIONES TURNO 1
# ─────────────────────────────────────────────
def elecciones_distrito(distrito):
    candidatos = obtener_candidatos(distrito["poblacion"])
    if not candidatos:
        return None, {}, 1.0
    votos, nulos = calcular_votos(distrito["poblacion"], candidatos)
    ganador = max(votos, key=votos.get)
    return ganador, votos, nulos

def elecciones_provincia(provincia):
    candidatos = obtener_candidatos(provincia["poblacion"])
    if not candidatos:
        return None, None, {}, 1.0
    votos, nulos = calcular_votos(provincia["poblacion"], candidatos)
    ordenados = sorted(votos.items(), key=lambda x: x[1], reverse=True)
    senA = ordenados[0][0] if len(ordenados) >= 1 else None
    senB = ordenados[1][0] if len(ordenados) >= 2 else None
    return senA, senB, votos, nulos

# ─────────────────────────────────────────────
# INTERFAZ STREAMLIT
# ─────────────────────────────────────────────
st.set_page_config(page_title="Simulador Político", layout="wide")
st.title("🗳️ Simulador Político — Turno 1")
st.caption("Marzo 2026 — Primera mitad")

if "estado" not in st.session_state:
    st.session_state.estado = None

if st.button("▶️ Iniciar Turno 1 (nueva simulación)"):
    distritos = distribuir_ideologia()
    provincias = calcular_provincias(distritos)
    pais = calcular_pais(provincias)
    presidente_color = random.choice(COLORES)

    # Elecciones
    resultados_distritos = []
    conteo_diputados = {c: 0 for c in COLORES}
    for d in distritos:
        ganador, votos, nulos = elecciones_distrito(d)
        resultados_distritos.append({
            "distrito": d["numero"], "ganador": ganador,
            "votos": votos, "nulos": nulos
        })
        if ganador:
            conteo_diputados[ganador] += 1

    resultados_provincias = []
    conteo_senadores = {c: 0 for c in COLORES}
    for p in provincias:
        senA, senB, votos, nulos = elecciones_provincia(p)
        resultados_provincias.append({
            "provincia": p["numero"], "senA": senA, "senB": senB,
            "votos": votos, "nulos": nulos
        })
        if senA: conteo_senadores[senA] += 1
        if senB: conteo_senadores[senB] += 1

    st.session_state.estado = {
        "distritos": distritos, "provincias": provincias, "pais": pais,
        "presidente": presidente_color,
        "resultados_distritos": resultados_distritos,
        "resultados_provincias": resultados_provincias,
        "conteo_diputados": conteo_diputados,
        "conteo_senadores": conteo_senadores
    }

# ─── MOSTRAR RESULTADOS ───
if st.session_state.estado:
    e = st.session_state.estado

    # Distribución nacional
    st.subheader("🌍 Distribución Ideológica Nacional")
    cols = st.columns(6)
    for i, color in enumerate(COLORES):
        with cols[i]:
            st.metric(color, f"{e['pais'][color]*100:.1f}%")

    st.divider()

    # Presidente
    st.subheader("🏛️ Presidente (designado aleatoriamente)")
    pres = e["presidente"]
    st.markdown(f"**Presidente:** :{pres.lower()}[{pres}]")

    st.divider()

    # Diputados
    st.subheader("🏠 Cámara de Diputados (150 escaños)")
    cols = st.columns(6)
    for i, color in enumerate(COLORES):
        with cols[i]:
            st.metric(color, f"{e['conteo_diputados'][color]} diputados")

    st.divider()

    # Senadores
    st.subheader("🏛️ Senado (60 escaños — Clase 1, provincias 1-10)")
    cols = st.columns(6)
    for i, color in enumerate(COLORES):
        with cols[i]:
            st.metric(color, f"{e['conteo_senadores'][color]} senadores")

    st.divider()

    # Detalle por provincia
    with st.expander("📋 Ver detalle por provincia"):
        for r in e["resultados_provincias"]:
            st.write(f"**Provincia {r['provincia']}** → Senador A: {r['senA']} | Senador B: {r['senB']}")
            votos_ord = sorted(r["votos"].items(), key=lambda x: x[1], reverse=True)
            for color, v in votos_ord:
                st.write(f"  - {color}: {v*100:.1f}%")
            st.write(f"  - Nulos: {r['nulos']*100:.1f}%")

    # Detalle por distrito
    with st.expander("📋 Ver detalle por distrito"):
        for r in e["resultados_distritos"]:
            st.write(f"**Distrito {r['distrito']}** → Diputado: {r['ganador']}")
