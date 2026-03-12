# ══════════════════════════════════════════════
# INTERFAZ: Political Interactive
# ══════════════════════════════════════════════
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from mecanicas import (
    inicializar_juego, avanzar_turno,
    turno_a_fecha, proximos_eventos, COLORES
)

# ── Colores hex por ideología ──
COLOR_HEX = {
    "Rojo":     "#e74c3c",
    "Verde":    "#27ae60",
    "Blanco":   "#bdc3c7",
    "Naranja":  "#e67e22",
    "Amarillo": "#f1c40f",
    "Azul":     "#2980b9"
}

# ══════════════════════════════════════════════
# HEMICICLO
# ══════════════════════════════════════════════
def dibujar_hemiciclo(conteo, total, titulo):
    escanos = []
    for color in COLORES:
        cantidad = conteo.get(color, 0)
        escanos += [COLOR_HEX[color]] * cantidad
    while len(escanos) < total:
        escanos.append("#cccccc")

    filas = 5
    puntos_por_fila = []
    for f in range(filas):
        n = total // filas + (1 if f < total % filas else 0)
        puntos_por_fila.append(n)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    idx = 0
    for f, n_puntos in enumerate(puntos_por_fila):
        radio = 0.5 + f * 0.12
        angulos = np.linspace(np.pi, 0, n_puntos)
        for angulo in angulos:
            if idx >= len(escanos):
                break
            x = radio * np.cos(angulo)
            y = radio * np.sin(angulo)
            ax.plot(x, y, "o",
                    color=escanos[idx],
                    markersize=6 - f * 0.3,
                    markeredgewidth=0.3,
                    markeredgecolor="#999999")
            idx += 1

    # Leyenda
    parches = []
    for color in COLORES:
        if conteo.get(color, 0) > 0:
            parches.append(mpatches.Patch(color=COLOR_HEX[color], label=f"{color}: {conteo.get(color,0)}"))
    ax.legend(handles=parches, loc="lower center", ncol=3,
              fontsize=8, framealpha=0.8, bbox_to_anchor=(0.5, -0.05))

    ax.set_title(titulo, color="black", fontsize=13, pad=10)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.2, 1.1)

    return fig

# ══════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Political Interactive",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Fondo oscuro general */
    .stApp {
        background-color: #1a1a2e;
        color: #e0e0e0;
    }
    /* Título */
    .titulo-juego {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #e0e0e0;
        letter-spacing: 0.2em;
        padding: 2rem 0 0.3rem 0;
    }
    .subtitulo {
        text-align: center;
        color: #888888;
        font-size: 1rem;
        margin-bottom: 3rem;
        letter-spacing: 0.1em;
    }
    /* Pestañas */
    .stTabs [data-baseweb="tab"] {
        color: #aaaaaa;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff;
        border-bottom: 2px solid #4a90d9;
    }
    /* Botones */
    .stButton > button {
        background-color: #16213e;
        color: #e0e0e0;
        border: 1px solid #4a90d9;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #4a90d9;
        color: white;
    }
    /* Métricas y texto */
    .stMetric {
        background-color: #16213e;
        border-radius: 8px;
        padding: 0.5rem;
    }
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #16213e;
        color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# UTILIDADES DE GUARDADO
# ══════════════════════════════════════════════
def inicializar_ranuras():
    if "ranura_1" not in st.session_state:
        st.session_state.ranura_1 = None
    if "ranura_2" not in st.session_state:
        st.session_state.ranura_2 = None

def etiqueta_ranura(ranura):
    if ranura is None:
        return "— Vacía —"
    turno = ranura["tiempo"]["turno"]
    fecha = turno_a_fecha(turno)["texto"]
    return f"Turno {turno} — {fecha}"

def guardar_en_ranura(estado, numero):
    if numero == 1:
        st.session_state.ranura_1 = estado
    else:
        st.session_state.ranura_2 = estado

def cargar_ranura(numero):
    if numero == 1:
        return st.session_state.ranura_1
    return st.session_state.ranura_2

def borrar_ranura(numero):
    if numero == 1:
        st.session_state.ranura_1 = None
    else:
        st.session_state.ranura_2 = None

# ══════════════════════════════════════════════
# PANTALLA DE INICIO
# ══════════════════════════════════════════════
def pantalla_inicio():
    inicializar_ranuras()

    st.markdown('<div class="titulo-juego">POLITICAL INTERACTIVE</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">SIMULADOR POLÍTICO</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("▶️ Nueva partida", use_container_width=True):
            st.session_state.estado   = inicializar_juego()
            st.session_state.en_juego = True
            st.rerun()

    st.markdown("---")
    st.markdown("#### 💾 Partidas guardadas")

    col_r1, col_r2 = st.columns(2)

    # ── Ranura 1 ──
    with col_r1:
        st.markdown(f"**Ranura 1:** {etiqueta_ranura(st.session_state.ranura_1)}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📂 Cargar", key="cargar_1",
                         disabled=st.session_state.ranura_1 is None,
                         use_container_width=True):
                st.session_state.estado   = cargar_ranura(1)
                st.session_state.en_juego = True
                st.rerun()
        with c2:
            if st.button("🗑️ Borrar", key="borrar_1",
                         disabled=st.session_state.ranura_1 is None,
                         use_container_width=True):
                borrar_ranura(1)
                st.rerun()

    # ── Ranura 2 ──
    with col_r2:
        st.markdown(f"**Ranura 2:** {etiqueta_ranura(st.session_state.ranura_2)}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📂 Cargar", key="cargar_2",
                         disabled=st.session_state.ranura_2 is None,
                         use_container_width=True):
                st.session_state.estado   = cargar_ranura(2)
                st.session_state.en_juego = True
                st.rerun()
        with c2:
            if st.button("🗑️ Borrar", key="borrar_2",
                         disabled=st.session_state.ranura_2 is None,
                         use_container_width=True):
                borrar_ranura(2)
                st.rerun()

# ══════════════════════════════════════════════
# PANTALLA DE JUEGO
# ══════════════════════════════════════════════
def pantalla_juego():
    inicializar_ranuras()
    estado = st.session_state.estado
    turno  = estado["tiempo"]["turno"]
    fecha  = turno_a_fecha(turno)["texto"]

    # ── Barra superior ──
    col_t, col_f, col_av, col_g1, col_g2, col_sal = st.columns([2, 2, 1, 1, 1, 1])
    with col_t:
        st.markdown("### 🏛️ POLITICAL INTERACTIVE")
    with col_f:
        st.markdown(f"**Turno {turno}** — {fecha}")
    with col_av:
        if st.button("▶️ Avanzar", use_container_width=True):
            st.session_state.estado = avanzar_turno(estado)
            st.rerun()
    with col_g1:
        if st.button("💾 Ranura 1", use_container_width=True):
            guardar_en_ranura(estado, 1)
            st.success("Guardado en Ranura 1")
    with col_g2:
        if st.button("💾 Ranura 2", use_container_width=True):
            guardar_en_ranura(estado, 2)
            st.success("Guardado en Ranura 2")
    with col_sal:
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state.en_juego = False
            st.rerun()

    st.divider()

    # ── Pestañas ──
    tab1, tab2 = st.tabs(["🏠 Oficina Presidencial", "🏛️ Congreso"])

    # ══════════════════════════════
    # PESTAÑA 1: OFICINA PRESIDENCIAL
    # ══════════════════════════════
    with tab1:
        presidente = estado["pais"].get("presidente", "Sin designar")
        st.markdown(f"### {presidente}")

        st.divider()

        # ── Próximas elecciones ──
        st.markdown("#### 📆 Próximas elecciones")
        proximos = proximos_eventos(turno, estado["provincias"], cantidad=4)
        nombres_evento = {
            "diputados":  "Diputados",
            "senadores":  "Senadores",
            "delegados":  "Delegados",
            "presidente": "Presidente"
        }
        for evento in proximos:
            tipos = evento["eventos"]
            tipos_texto = []
            for k, v in tipos.items():
                if k == "senadores" and v:
                    tipos_texto.append("Senadores")
                elif v and k != "senadores":
                    tipos_texto.append(nombres_evento[k])
            faltan = evento["turno"] - turno
            st.markdown(
                f"- **{evento['fecha']}** "
                f"(Turno {evento['turno']}, faltan **{faltan} turnos**): "
                f"{', '.join(tipos_texto)}"
            )

        st.divider()

        # ── Historial: solo último turno ──
        with st.expander("📜 Historial del último turno", expanded=True):
            log = estado.get("log", [])
            if log:
                # Mostrar solo las entradas del último turno
                ultimo_bloque = []
                for entrada in reversed(log):
                    ultimo_bloque.append(entrada)
                    if entrada.startswith("Turno") and len(ultimo_bloque) > 1:
                        break
                for entrada in reversed(ultimo_bloque):
                    st.markdown(f"- {entrada}")

    # ══════════════════════════════
    # PESTAÑA 2: CONGRESO
    # ══════════════════════════════
    with tab2:

        # ── Diputados ──
        st.markdown("### 🏠 Cámara de Diputados — 150 escaños")
        conteo_d = estado["conteo_diputados"]
        col_h, col_l = st.columns([2, 1])
        with col_h:
            fig_d = dibujar_hemiciclo(conteo_d, 150, "Cámara de Diputados")
            st.pyplot(fig_d)
        with col_l:
            st.markdown("**Composición**")
            for color in COLORES:
                n   = conteo_d.get(color, 0)
                pct = round(n / 150 * 100, 1)
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} escaños ({pct}%)',
                    unsafe_allow_html=True
                )

        st.divider()

        # ── Senadores ──
        st.markdown("### 🏛️ Senado — 60 escaños")
        conteo_s = estado["conteo_senadores"]
        col_h2, col_l2 = st.columns([2, 1])
        with col_h2:
            fig_s = dibujar_hemiciclo(conteo_s, 60, "Senado")
            st.pyplot(fig_s)
        with col_l2:
            st.markdown("**Composición**")
            for color in COLORES:
                n   = conteo_s.get(color, 0)
                pct = round(n / 60 * 100, 1) if n > 0 else 0
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} escaños ({pct}%)',
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════
if "en_juego" not in st.session_state:
    st.session_state.en_juego = False

if st.session_state.en_juego:
    pantalla_juego()
else:
    pantalla_inicio()
