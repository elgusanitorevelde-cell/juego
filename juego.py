# ══════════════════════════════════════════════
# INTERFAZ: Political Interactive
# ══════════════════════════════════════════════
import streamlit as st
import matplotlib.pyplot as plt
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
    """
    Dibuja un hemiciclo con puntos de colores.
    conteo: dict {color: cantidad de escaños}
    total: total de escaños
    titulo: título del gráfico
    """
    # Construir lista de colores en orden de escaños
    escanos = []
    for color in COLORES:
        cantidad = conteo.get(color, 0)
        escanos += [COLOR_HEX[color]] * cantidad

    # Rellenar vacíos si hay escaños sin asignar
    while len(escanos) < total:
        escanos.append("#ecf0f1")

    # Calcular posiciones en hemiciclo
    filas = 5
    puntos_por_fila = []
    restantes = total
    for f in range(filas):
        n = total // filas + (1 if f < total % filas else 0)
        puntos_por_fila.append(n)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

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
                    markersize=6 - f * 0.5,
                    markeredgewidth=0.2,
                    markeredgecolor="#1e1e2e")
            idx += 1

    ax.set_title(titulo, color="white", fontsize=13, pad=10)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.15, 1.1)

    return fig

# ══════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Political Interactive",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS básico ──
st.markdown("""
    <style>
    .titulo-juego {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: white;
        letter-spacing: 0.15em;
        padding: 1rem 0 0.2rem 0;
    }
    .subtitulo {
        text-align: center;
        color: #aaaaaa;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PANTALLA DE INICIO
# ══════════════════════════════════════════════
def pantalla_inicio():
    st.markdown('<div class="titulo-juego">POLITICAL INTERACTIVE</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Simulador político</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("▶️ Iniciar partida", use_container_width=True):
            st.session_state.estado = inicializar_juego()
            st.session_state.en_juego = True
            st.rerun()

        partida_guardada = st.session_state.get("partida_guardada", None)

        if partida_guardada:
            if st.button("📂 Cargar partida", use_container_width=True):
                st.session_state.estado = partida_guardada
                st.session_state.en_juego = True
                st.rerun()
            if st.button("🗑️ Borrar partida", use_container_width=True):
                st.session_state.partida_guardada = None
                st.success("Partida borrada.")
                st.rerun()
        else:
            st.button("📂 Cargar partida", disabled=True, use_container_width=True)
            st.button("🗑️ Borrar partida", disabled=True, use_container_width=True)

# ══════════════════════════════════════════════
# PANTALLA DE JUEGO
# ══════════════════════════════════════════════
def pantalla_juego():
    estado = st.session_state.estado
    turno  = estado["tiempo"]["turno"]
    fecha  = turno_a_fecha(turno)["texto"]

    # ── Barra superior ──
    col_titulo, col_turno, col_acciones = st.columns([3, 2, 2])
    with col_titulo:
        st.markdown("### 🏛️ Political Interactive")
    with col_turno:
        st.markdown(f"**Turno {turno}** — {fecha}")
    with col_acciones:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("▶️ Avanzar"):
                st.session_state.estado = avanzar_turno(estado)
                st.rerun()
        with col_b:
            if st.button("💾 Guardar"):
                st.session_state.partida_guardada = estado
                st.success("Guardado.")
        with col_c:
            if st.button("🚪 Salir"):
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
        st.markdown(f"### Presidente: {presidente}")

        st.divider()

        # Próximas elecciones
        st.markdown("#### 📆 Próximas elecciones")
        proximos = proximos_eventos(turno, estado["provincias"], cantidad=4)
        for evento in proximos:
            tipos = evento["eventos"]
            nombres = {
                "diputados":   "Diputados",
                "senadores":   "Senadores",
                "delegados":   "Delegados",
                "presidente":  "Presidente"
            }
            tipos_texto = ", ".join(
                nombres[k] for k, v in tipos.items()
                if v and k != "senadores"
            )
            if tipos.get("senadores"):
                tipos_texto += ", Senadores"
            faltan = evento["turno"] - turno
            st.markdown(
                f"- **{evento['fecha']}** (Turno {evento['turno']}, "
                f"faltan **{faltan} turnos**): {tipos_texto}"
            )

        st.divider()

        # Historial de eventos
        st.markdown("#### 📜 Historial de eventos")
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
                n = conteo_d.get(color, 0)
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

        col_hem2, col_ley2 = st.columns([2, 1])
        with col_hem2:
            fig_s = dibujar_hemiciclo(conteo_s, 60, "Senado")
            st.pyplot(fig_s)
        with col_ley2:
            st.markdown("**Composición**")
            for color in COLORES:
                n = conteo_s.get(color, 0)
                pct = round(n / 60 * 100, 1) if n > 0 else 0
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} escaños ({pct}%)',
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
                    conteo_del[color] += 1

        col_hem3, col_ley3 = st.columns([2, 1])
        with col_hem3:
            fig_del = dibujar_hemiciclo(conteo_del, 90, "Delegados")
            st.pyplot(fig_del)
        with col_ley3:
            st.markdown("**Composición**")
            for color in COLORES:
                n = conteo_del.get(color, 0)
                pct = round(n / 90 * 100, 1) if n > 0 else 0
                hex_c = COLOR_HEX[color]
                st.markdown(
                    f'<span style="color:{hex_c};">⬤</span> '
                    f'**{color}**: {n} delegados ({pct}%)',
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

---

También actualiza `requirements.txt` con esto:
```
streamlit
matplotlib
numpy
