# ══════════════════════════════════════════════
# BLOQUE 0: Configuración e importaciones
# ══════════════════════════════════════════════
import streamlit as st
import random

# ══════════════════════════════════════════════
# BLOQUE 1: Estructura del mundo
# ══════════════════════════════════════════════

# ── Constantes ──
POBLACION_DISTRITO  = 100_000
POBLACION_PROVINCIA = 500_000
POBLACION_TOTAL     = 15_000_000
NUM_DISTRITOS       = 150
NUM_PROVINCIAS      = 30
DISTRITOS_POR_PROVINCIA = 5  # 5 distritos × 30 provincias = 150 distritos

# ── Construcción del mundo ──
def crear_distritos():
    """
    Crea 150 distritos numerados del 1 al 150.
    Cada distrito tiene:
      - número (1 a 150)
      - población fija de 100.000
      - 1 diputado (cargo, inicialmente vacío)
    """
    distritos = []
    for i in range(1, NUM_DISTRITOS + 1):
        distritos.append({
            "numero":    i,
            "poblacion": POBLACION_DISTRITO,
            "diputado":  None  # Se llenará en el bloque electoral
        })
    return distritos

def crear_provincias(distritos):
    """
    Crea 30 provincias numeradas del 1 al 30.
    Cada provincia agrupa 5 distritos consecutivos.
    Cada provincia tiene:
      - número (1 a 30)
      - lista de 5 distritos
      - población = suma de sus 5 distritos (500.000)
      - senador_A y senador_B (inicialmente vacíos)
      - delegado_A, delegado_B, delegado_C (inicialmente vacíos)
    """
    provincias = []
    for i in range(NUM_PROVINCIAS):
        grupo = distritos[i * DISTRITOS_POR_PROVINCIA : (i + 1) * DISTRITOS_POR_PROVINCIA]
        provincias.append({
            "numero":     i + 1,
            "distritos":  grupo,
            "poblacion":  sum(d["poblacion"] for d in grupo),  # = 500.000
            "senador_A":  None,
            "senador_B":  None,
            "delegado_A": None,
            "delegado_B": None,
            "delegado_C": None
        })
    return provincias

def crear_pais(provincias):
    """
    El país es la suma de las 30 provincias.
    Tiene:
      - población total (15.000.000)
      - presidente (inicialmente vacío)
    """
    return {
        "poblacion":  sum(p["poblacion"] for p in provincias),  # = 15.000.000
        "presidente": None
    }

# ── Función principal de inicialización ──
def inicializar_mundo():
    distritos = crear_distritos()
    provincias = crear_provincias(distritos)
    pais       = crear_pais(provincias)
    return distritos, provincias, pais


# ══════════════════════════════════════════════
# INTERFAZ STREAMLIT — Prueba del Bloque 1
# ══════════════════════════════════════════════
st.set_page_config(page_title="Simulador Político", layout="wide")
st.title("🗳️ Simulador Político")
st.subheader("Bloque 1 — Estructura del mundo")

if st.button("▶️ Inicializar mundo"):
    distritos, provincias, pais = inicializar_mundo()
    st.session_state.distritos  = distritos
    st.session_state.provincias = provincias
    st.session_state.pais       = pais

if "pais" in st.session_state:
    pais      = st.session_state.pais
    provincias = st.session_state.provincias
    distritos  = st.session_state.distritos

    # País
    st.markdown(f"### 🌍 País — Población total: {pais['poblacion']:,}")
    st.write(f"Presidente: {pais['presidente'] or 'Sin designar'}")

    st.divider()

    # Provincias
    st.markdown("### 🏙️ Provincias")
    for p in provincias:
        with st.expander(f"Provincia {p['numero']} — Población: {p['poblacion']:,}"):
            st.write(f"Senador A: {p['senador_A'] or 'Vacío'} | Senador B: {p['senador_B'] or 'Vacío'}")
            st.write(f"Delegado A: {p['delegado_A'] or 'Vacío'} | Delegado B: {p['delegado_B'] or 'Vacío'} | Delegado C: {p['delegado_C'] or 'Vacío'}")
            st.write("**Distritos:**")
            for d in p["distritos"]:
                st.write(f"  • Distrito {d['numero']} — Población: {d['poblacion']:,} — Diputado: {d['diputado'] or 'Vacío'}")
