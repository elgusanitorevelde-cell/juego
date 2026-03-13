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
                    markeredgewidth=0.8,
                    markeredgecolor="black")
            idx += 1

    ax.set_title(titulo, color="black", fontsize=13, pad=10)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.15, 1.1)
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
        background-color: #0f0f1a;
        color: #e0e0e0;
    }
    /* Fondo oscuro en contenedores */
    .block-container {
        background-color: #0f0f1a;
    }
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a2e;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #aaaaaa;
    }
    .stTabs [aria-selected="true"] {
        color: white;
        background-color: #2e2e4e;
        border-radius: 6px;
    }
    /* Título principal */
    .titulo-juego {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: white;
        letter-spacing: 0.2em;
        padding: 2rem 0 0.3rem 0;
        text-transform: uppercase;
    }
    .subtitulo {
        text-align: center;
        color: #888888;
        font-size: 1rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.1em;
    }
    /* Botones */
    .stButton > button {
        background-color: #1e1e3e;
        color: white;
        border: 1px solid #444466;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #2e2e5e;
        border-color: #6666aa;
    }
    /* Noticia */
    .noticia-box {
        background-color: #1a1a2e;
        border-left: 4px solid #e74c3c;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        margin-bottom: 0.8rem;
        color: #e0e0e0;
    }
    /* Ranura de guardado */
    .ranura-box {
        background-color: #1a1a2e;
        border: 1px solid #333355;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
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

def info_ranura(ranura):
    if ranura is None:
        return "Vacía"
    turno = ranura["tiempo"]["turno"]
    fecha = turno_a_fecha(turno)["texto"]
    return f"Turno {turno} — {fecha}"

# ══════════════════════════════════════════════
# PANTALLA DE INICIO
# ══════════════════════════════════════════════
def pantalla_inicio():
    inicializar_ranuras()

    st.markdown('<div class="titulo-juego">Political Interactive</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Simulador político</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:

        # ── Iniciar partida ──
        if st.button("▶️ Iniciar nueva partida", use_container_width=True):
            st.session_state.estado   = inicializar_juego()
            st.session_state.en_juego = True
            st.rerun()

        st.markdown("---")

        # ── Ranura 1 ──
        st.markdown(
            f'<div class="ranura-box">💾 <b>Ranura 1</b> — {info_ranura(st.session_state.ranura_1)}</div>',
            unsafe_allow_html=True
        )
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📂 Cargar Ranura 1",
                         disabled=st.session_state.ranura_1 is None,
                         use_container_width=True):
                st.session_state.estado   = st.session_state.ranura_1
                st.session_state.en_juego = True
                st.rerun()
        with col_b:
            if st.button("🗑️ Borrar Ranura 1",
                         disabled=st.session_state.ranura_1 is None,
                         use_container_width=True):
                st.session_state.ranura_1 = None
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Ranura 2 ──
        st.markdown(
            f'<div class="ranura-box">💾 <b>Ranura 2</b> — {info_ranura(st.session_state.ranura_2)}</div>',
            unsafe_allow_html=True
        )
        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("📂 Cargar Ranura 2",
                         disabled=st.session_state.ranura_2 is None,
                         use_container_width=True):
                st.session_state.estado   = st.session_state.ranura_2
                st.session_state.en_juego = True
                st.rerun()
        with col_d:
            if st.button("🗑️ Borrar Ranura 2",
                         disabled=st.session_state.ranura_2 is None,
                         use_container_width=True):
                st.session_state.ranura_2 = None
                st.rerun()

# ══════════════════════════════════════════════
# NOTICIAS ELECTORALES
# ══════════════════════════════════════════════
def mostrar_noticias(estado):

    hay_noticias = False

    # ── Resultado legislativo ──
    res_leg = estado.get("ultimo_resultado_legislativo")
    if res_leg:
        hay_noticias = True
        tipo = res_leg["tipo"]

        if tipo == "diputados":
            titulo = "Elecciones Legislativas — Nueva composición de la Cámara de Diputados"
        elif tipo == "senadores":
            titulo = "Elecciones Legislativas — Nueva composición del Senado"
        else:
            titulo = "Elecciones Legislativas — Nueva composición del Congreso"

        st.markdown(
            f'<div class="noticia-box">📰 <b>Noticias de última hora:</b> {titulo}</div>',
            unsafe_allow_html=True
        )

        # Diputados
        if tipo in ["diputados", "ambos"]:
            conteo_d = res_leg["conteo_diputados"]
            st.markdown("**🏠 Cámara de Diputados:**")
            for color in COLORES:
                n = conteo_d.get(color, 0)
                if n > 0:
                    pct   = round(n / 150 * 100, 1)
                    hex_c = COLOR_HEX[color]
                    st.markdown(
                        f'<span style="color:{hex_c};">⬤</span> '
                        f'**{color}**: {n} escaños ({pct}%)',
                        unsafe_allow_html=True
                    )

        # Senadores
        if tipo in ["senadores", "ambos"]:
            conteo_s = res_leg["conteo_senadores"]
            total_s  = sum(conteo_s.values())
            st.markdown("**🏛️ Senado:**")
            for color in COLORES:
                n = conteo_s.get(color, 0)
                if n > 0:
                    pct   = round(n / 60 * 100, 1)
                    hex_c = COLOR_HEX[color]
                    st.markdown(
                        f'<span style="color:{hex_c};">⬤</span> '
                        f'**{color}**: {n} escaños ({pct}%)',
                        unsafe_allow_html=True
                    )

    # ── Resultado delegados ──
    res_del = estado.get("ultimo_resultado_delegados")
    if res_del:
        hay_noticias = True
        st.markdown(
            '<div class="noticia-box">📰 <b>Noticias de última hora:</b> '
            'Composición del Colegio de Delegados</div>',
            unsafe_allow_html=True
        )
        conteo_del = res_del["conteo_delegados"]
        for color in COLORES:
            n = conteo_del.get(color, 0)
            if n > 0:
                pct   = round(n / 90 * 100, 1)
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} delegados ({pct}%)',
                    unsafe_allow_html=True
                )

    # ── Resultado presidencial ──
    res_pres = estado.get("ultimo_resultado_presidente")
    if res_pres:
        hay_noticias = True
        ganador = res_pres.get("ganador")
        tipo    = res_pres.get("tipo")

        if tipo == "delegados_sin_ganador":
            st.markdown(
                '<div class="noticia-box">📰 <b>Noticias de última hora:</b> '
                'Elección Presidencial — Ningún candidato alcanzó 46 votos. '
                'Se convoca segunda vuelta provincial.</div>',
                unsafe_allow_html=True
            )
        elif tipo == "provincial":
            st.markdown(
                f'<div class="noticia-box">📰 <b>Noticias de última hora:</b> '
                f'Segunda Vuelta Presidencial — Ganador: <b>{ganador}</b></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="noticia-box">📰 <b>Noticias de última hora:</b> '
                f'Elección Presidencial — Ganador: <b>{ganador}</b></div>',
                unsafe_allow_html=True
            )

        # Resultado detallado por candidato
        resultado = res_pres.get("resultado", [])
        if resultado:
            st.markdown("**Resultado por candidato:**")
            total_votos = sum(r["votos"] for r in resultado)
            for r in resultado:
                color  = r["color"]
                votos  = r["votos"]
                pct    = round(votos / total_votos * 100, 1) if total_votos > 0 else 0
                hex_c  = COLOR_HEX.get(color, "#ffffff")
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {votos} votos ({pct}%)',
                    unsafe_allow_html=True
                )

    if not hay_noticias:
        st.markdown("_Sin noticias electorales en el turno actual._")
# ══════════════════════════════════════════════
# PANTALLA DE JUEGO
# ══════════════════════════════════════════════
def pantalla_juego():
    inicializar_ranuras()
    estado = st.session_state.estado
    turno  = estado["tiempo"]["turno"]
    fecha  = turno_a_fecha(turno)["texto"]

    # ── Barra superior ──
    col_titulo, col_turno, col_acciones = st.columns([3, 2, 3])
    with col_titulo:
        st.markdown("### 🏛️ Political Interactive")
    with col_turno:
        st.markdown(f"**Turno {turno}** — {fecha}")
    with col_acciones:
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        with col_a:
            if st.button("▶️", help="Avanzar turno"):
                st.session_state.estado = avanzar_turno(estado)
                st.rerun()
        with col_b:
            if st.button("💾1", help="Guardar en Ranura 1"):
                st.session_state.ranura_1 = estado
                st.success("Guardado en Ranura 1.")
        with col_c:
            if st.button("💾2", help="Guardar en Ranura 2"):
                st.session_state.ranura_2 = estado
                st.success("Guardado en Ranura 2.")
        with col_d:
            if st.button("🚪", help="Salir al menú"):
                st.session_state.en_juego = False
                st.rerun()

    st.divider()

    # ── Pestañas principales ──
    tab1, tab2 = st.tabs(["🏠 Oficina Presidencial", "🏛️ Congreso"])

    # ══════════════════════════════
    # PESTAÑA 1: OFICINA PRESIDENCIAL
    # ══════════════════════════════
    with tab1:
        presidente = estado["pais"].get("presidente", "Sin designar")
        st.markdown(f"### {presidente}")
        st.divider()
        st.markdown("#### 📆 Próximas elecciones")
        proximos = proximos_eventos(turno, estado["provincias"], cantidad=4)
        nombres = {
            "diputados":  "Diputados",
            "senadores":  "Senadores",
            "delegados":  "Delegados",
            "presidente": "Presidente",
            "asuncion":   "Asunción Presidencial"
        }
        for evento in proximos:
            tipos = evento["eventos"]
            tipos_texto = ", ".join(
                nombres[k] for k, v in tipos.items()
                if k in nombres and (
                    (k != "senadores" and v) or
                    (k == "senadores" and v)
                )
            )
            faltan = evento["turno"] - turno
            st.markdown(
                f"- **{evento['fecha']}** — "
                f"Turno {evento['turno']} "
                f"(faltan **{faltan} turnos**): {tipos_texto}"
            )
        # Historial con noticias electorales expandible
        with st.expander("📰 Noticias y resultados electorales", expanded=True):
            mostrar_noticias(estado)

        with st.expander("📜 Historial completo de eventos"):
            for entrada in reversed(estado["log"]):
                st.markdown(f"- {entrada}")

    # ══════════════════════════════
    # PESTAÑA 2: CONGRESO
    # ══════════════════════════════
    with tab2:

        # ── Diputados ──
        st.markdown("### 🏠 Cámara de Diputados — 150 escaños")
        conteo_d = estado["conteo_diputados"]
        col_hem, col_ley = st.columns([2, 1])
        with col_hem:
            fig_d = dibujar_hemiciclo(conteo_d, 150, "Cámara de Diputados")
            st.pyplot(fig_d)
        with col_ley:
            st.markdown("**Composición**")
            for color in COLORES:
                n     = conteo_d.get(color, 0)
                pct   = round(n / 150 * 100, 1)
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} ({pct}%)',
                    unsafe_allow_html=True
                )

        st.divider()

        # ── Senadores ──
        st.markdown("### 🏛️ Senado — 60 escaños")
        conteo_s = estado["conteo_senadores"]
        col_hem2, col_ley2 = st.columns([2, 1])
        with col_hem2:
            fig_s = dibujar_hemiciclo(conteo_s, 60, "Senado")
            st.pyplot(fig_s)
        with col_ley2:
            st.markdown("**Composición**")
            for color in COLORES:
                n     = conteo_s.get(color, 0)
                pct   = round(n / 60 * 100, 1) if n > 0 else 0
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} ({pct}%)',
                    unsafe_allow_html=True
                )

        st.divider()

        # ── Delegados ──
        st.markdown("### 🗳️ Delegados — 90 delegados")
        conteo_del = {c: 0 for c in COLORES}
        for p in estado["provincias"]:
            for cargo in ["delegado_A", "delegado_B", "delegado_C"]:
                d = p.get(cargo)
                if d:
                    color = d.split("(")[-1].replace(")", "").strip()
                    if color in conteo_del:
                        conteo_del[color] += 1
        col_hem3, col_ley3 = st.columns([2, 1])
        with col_hem3:
            fig_del = dibujar_hemiciclo(conteo_del, 90, "Delegados")
            st.pyplot(fig_del)
        with col_ley3:
            st.markdown("**Composición**")
            for color in COLORES:
                n     = conteo_del.get(color, 0)
                pct   = round(n / 90 * 100, 1) if n > 0 else 0
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} ({pct}%)',
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
