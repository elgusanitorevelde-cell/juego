# ══════════════════════════════════════════════
# BLOQUE 0: Importaciones
# ══════════════════════════════════════════════
import random

# ══════════════════════════════════════════════
# BLOQUE 1: Estructura del mundo
# ══════════════════════════════════════════════

# ── Constantes ──
POBLACION_DISTRITO      = 100_000
POBLACION_PROVINCIA     = 500_000
POBLACION_TOTAL         = 15_000_000
NUM_DISTRITOS           = 150
NUM_PROVINCIAS          = 30
DISTRITOS_POR_PROVINCIA = 5  # 5 distritos × 30 provincias = 150 distritos

# ── Funciones ──
def crear_distritos():
    """
    Crea 150 distritos numerados del 1 al 150.
    Cada distrito tiene:
      - número (1 a 150)
      - población fija de 100.000
      - 1 diputado (vacío, se llenará en el bloque electoral)
    """
    distritos = []
    for i in range(1, NUM_DISTRITOS + 1):
        distritos.append({
            "numero":    i,
            "poblacion": POBLACION_DISTRITO,
            "diputado":  None
        })
    return distritos

def crear_provincias(distritos):
    """
    Crea 30 provincias numeradas del 1 al 30.
    Cada provincia agrupa 5 distritos consecutivos.
    Cada provincia tiene:
      - número (1 a 30)
      - lista de sus 5 distritos
      - población = suma de sus 5 distritos (500.000)
      - 2 senadores (vacíos)
      - 3 delegados (vacíos)
    """
    provincias = []
    for i in range(NUM_PROVINCIAS):
        grupo = distritos[i * DISTRITOS_POR_PROVINCIA : (i + 1) * DISTRITOS_POR_PROVINCIA]
        provincias.append({
            "numero":     i + 1,
            "distritos":  grupo,
            "poblacion":  sum(d["poblacion"] for d in grupo),
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
      - 1 presidente (vacío)
    """
    return {
        "poblacion":  sum(p["poblacion"] for p in provincias),
        "presidente": None
    }

def inicializar_mundo():
    """
    Función principal que construye el mundo completo.
    Devuelve: distritos, provincias, pais
    """
    distritos  = crear_distritos()
    provincias = crear_provincias(distritos)
    pais       = crear_pais(provincias)
    return distritos, provincias, pais
    # ══════════════════════════════════════════════
# BLOQUE 2: Ideología y sistema de afinidades
# ══════════════════════════════════════════════

# ── Constantes ──
COLORES = ["Rojo", "Verde", "Blanco", "Naranja", "Amarillo", "Azul"]

AFINIDADES = {
    "Rojo":     ["Blanco", "Verde"],
    "Verde":    ["Blanco", "Rojo", "Naranja"],
    "Blanco":   ["Naranja", "Verde", "Rojo", "Amarillo"],
    "Naranja":  ["Blanco", "Amarillo", "Azul", "Verde"],
    "Amarillo": ["Naranja", "Blanco", "Azul"],
    "Azul":     ["Naranja", "Amarillo"]
}

# Pesos fijos en orden jerárquico (proporción, no porcentaje)
PESOS_AFINIDAD = [80, 60, 40, 20]

# Porcentaje mínimo de población por color en la distribución inicial
MIN_POBLACION_COLOR = 0.05  # 5%

# Porcentaje de voto nulo para colores sin candidato
VOTO_NULO_SIN_CANDIDATO = 0.15  # 15%

# ── Distribución ideológica ──
def distribuir_ideologia_distrito():
    """
    Distribuye la población de un distrito aleatoriamente entre los 6 colores.
    Regla: cada color debe tener al menos el 5% de la población.
    Devuelve un dict {color: proporción} donde la suma es 1.0
    """
    while True:
        # Generar 5 cortes aleatorios entre 1 y 99
        cortes = sorted(random.sample(range(1, 100), 5))
        partes = (
            [cortes[0]] +
            [cortes[i] - cortes[i-1] for i in range(1, 5)] +
            [100 - cortes[4]]
        )
        # Verificar que cada parte sea al menos 5%
        if all(p >= 5 for p in partes):
            return {COLORES[i]: partes[i] / 100 for i in range(6)}

def asignar_ideologia_a_distritos(distritos):
    """
    Asigna una distribución ideológica a cada distrito.
    Agrega la clave 'ideologia' a cada distrito:
      {color: proporción} — proporciones suman 1.0
    """
    for d in distritos:
        d["ideologia"] = distribuir_ideologia_distrito()
    return distritos

def calcular_ideologia_provincia(provincia):
    """
    La ideología de una provincia es el promedio
    de las ideologías de sus 5 distritos.
    Devuelve un dict {color: proporción}
    """
    ideologia = {}
    for color in COLORES:
        ideologia[color] = sum(
            d["ideologia"][color] for d in provincia["distritos"]
        ) / len(provincia["distritos"])
    return ideologia

def calcular_ideologia_pais(provincias):
    """
    La ideología del país es el promedio
    de las ideologías de las 30 provincias.
    Devuelve un dict {color: proporción}
    """
    ideologia = {}
    for color in COLORES:
        ideologia[color] = sum(
            p["ideologia"][color] for p in provincias
        ) / len(provincias)
    return ideologia

def asignar_ideologia_a_provincias_y_pais(provincias):
    """
    Calcula y asigna la ideología a cada provincia y al país.
    Agrega la clave 'ideologia' a cada provincia y devuelve
    la ideología del país.
    """
    for p in provincias:
        p["ideologia"] = calcular_ideologia_provincia(p)
    ideologia_pais = calcular_ideologia_pais(provincias)
    return provincias, ideologia_pais

# ── Sistema de afinidades y cálculo de votos ──
def calcular_votos(ideologia, candidatos):
    """
    Calcula la distribución de votos dado:
      - ideologia: dict {color: proporción} del territorio
      - candidatos: lista de colores que presentan candidato

    Reglas:
      - Colores CON candidato votan 100% por su propio candidato
      - Colores SIN candidato:
          * 15% voto nulo
          * 85% redistribuido por afinidades (pesos normalizados)
          * Si no hay afinidad posible: 100% nulo

    Devuelve:
      - votos: dict {color: proporción} solo para candidatos
      - nulos: proporción de votos nulos (0.0 a 1.0)
    """
    votos = {c: 0.0 for c in candidatos}
    nulos = 0.0

    for color, proporcion in ideologia.items():
        if color in candidatos:
            # Vota por su propio candidato
            votos[color] += proporcion
        else:
            # Sin candidato: 15% nulo
            nulos += proporcion * VOTO_NULO_SIN_CANDIDATO
            redistribuible = proporcion * (1 - VOTO_NULO_SIN_CANDIDATO)

            # Filtrar afinidades que tienen candidato
            afinidades_validas = [
                a for a in AFINIDADES[color] if a in candidatos
            ]

            if not afinidades_validas:
                # Sin afinidad posible: 100% nulo
                nulos += redistribuible
            else:
                # Aplicar pesos jerárquicos y normalizar
                pesos = PESOS_AFINIDAD[:len(afinidades_validas)]
                total_pesos = sum(pesos)
                for i, af in enumerate(afinidades_validas):
                    votos[af] += redistribuible * (pesos[i] / total_pesos)

    return votos, nulos
# ══════════════════════════════════════════════
# BLOQUE 3: Estructura temporal y ciclo electoral
# ══════════════════════════════════════════════

# ── Constantes de tiempo ──
TURNO_INICIAL = 1
MES_INICIAL   = 3    # Marzo
ANIO_INICIAL  = 2026
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# ── Constantes electorales ──
FRECUENCIA_DIPUTADOS    = 48
FRECUENCIA_SENADORES_C1 = 48
FRECUENCIA_SENADORES_C2 = 96
FRECUENCIA_SENADORES_C3 = 144
FRECUENCIA_DELEGADOS    = 94
FRECUENCIA_PRESIDENTE   = 96

# ── Variables primarias ──
def inicializar_tiempo():
    """
    Devuelve el estado inicial del tiempo.
    Variables primarias: turno, mes, año.
    """
    return {
        "turno": TURNO_INICIAL,
        "mes":   MES_INICIAL,
        "anio":  ANIO_INICIAL
    }

def turno_a_fecha(turno):
    """
    Convierte un número de turno a su fecha correspondiente.
    Turno 1 = Primera mitad de Marzo 2026.
    Un turno = medio mes. Dos turnos = un mes.
    Devuelve un dict {mitad, mes, anio, texto}
    """
    meses_transcurridos = (turno - 1) // 2
    mitad = "Primera mitad" if turno % 2 != 0 else "Segunda mitad"
    mes_indice = (MES_INICIAL - 1 + meses_transcurridos) % 12
    anios_extra = (MES_INICIAL - 1 + meses_transcurridos) // 12
    return {
        "mitad": mitad,
        "mes":   MESES[mes_indice],
        "anio":  ANIO_INICIAL + anios_extra,
        "texto": f"{mitad} de {MESES[mes_indice]}, {ANIO_INICIAL + anios_extra}"
    }

def avanzar_tiempo(tiempo):
    """
    Avanza el tiempo en un turno.
    Recalcula mes y año según el nuevo turno.
    """
    nuevo_turno = tiempo["turno"] + 1
    fecha = turno_a_fecha(nuevo_turno)
    return {
        "turno": nuevo_turno,
        "mes":   fecha["mes"],
        "anio":  fecha["anio"]
    }

# ── Asignación aleatoria de clases de senadores ──
def asignar_clases_senadores(provincias):
    """
    Divide las 30 provincias aleatoriamente en 3 clases iguales de 10 provincias cada una.
    Clase 1: elección cada 48 turnos  (desde turno 1)
    Clase 2: elección cada 96 turnos  (desde turno 97)
    Clase 3: elección cada 144 turnos (desde turno 145)
    Agrega la clave 'clase_senadores' a cada provincia (1, 2 o 3).
    """
    numeros = [p["numero"] for p in provincias]
    random.shuffle(numeros)
    clases = {
        numeros[i]: 1 if i < 10 else 2 if i < 20 else 3
        for i in range(30)
    }
    for p in provincias:
        p["clase_senadores"] = clases[p["numero"]]
    return provincias

# ── Calendario electoral ──
def elecciones_en_turno(turno, provincias):
    """
    Determina qué elecciones ocurren en un turno dado.
    Devuelve un dict con los eventos y las provincias afectadas.
    Ejemplo:
    {
        "diputados": True,
        "senadores": [1, 5, 12, ...],  # números de provincia
        "delegados": True,
        "presidente": True
    }
    """
    eventos = {
        "diputados":  False,
        "senadores":  [],
        "delegados":  False,
        "presidente": False
    }

    # Turno 1: elecciones iniciales
    if turno == 1:
        eventos["diputados"] = True
        # Solo provincias de clase 1 eligen senadores en turno 1
        eventos["senadores"] = [
            p["numero"] for p in provincias if p["clase_senadores"] == 1
        ]
        return eventos

    # Diputados: cada 48 turnos desde turno 1
    if (turno - 1) % FRECUENCIA_DIPUTADOS == 0:
        eventos["diputados"] = True

    # Senadores Clase 1: cada 48 turnos desde turno 1
    if (turno - 1) % FRECUENCIA_SENADORES_C1 == 0:
        eventos["senadores"] += [
            p["numero"] for p in provincias if p["clase_senadores"] == 1
        ]

    # Senadores Clase 2: cada 96 turnos desde turno 97
    if turno >= 97 and (turno - 97) % FRECUENCIA_SENADORES_C2 == 0:
        eventos["senadores"] += [
            p["numero"] for p in provincias if p["clase_senadores"] == 2
        ]

    # Senadores Clase 3: cada 144 turnos desde turno 145
    if turno >= 145 and (turno - 145) % FRECUENCIA_SENADORES_C3 == 0:
        eventos["senadores"] += [
            p["numero"] for p in provincias if p["clase_senadores"] == 3
        ]

    # Delegados: cada 94 turnos desde turno 95
    if turno >= 95 and (turno - 95) % FRECUENCIA_DELEGADOS == 0:
        eventos["delegados"] = True

    # Presidente: cada 96 turnos desde turno 97
    if turno >= 97 and (turno - 97) % FRECUENCIA_PRESIDENTE == 0:
        eventos["presidente"] = True

    return eventos

def proximos_eventos(turno, provincias, cantidad=3):
    """
    Devuelve los próximos eventos electorales a partir del turno dado.
    Útil para mostrar al jugador qué elecciones se aproximan.
    """
    proximos = []
    t = turno + 1
    while len(proximos) < cantidad:
        eventos = elecciones_en_turno(t, provincias)
        hay_evento = (
            eventos["diputados"] or
            eventos["senadores"] or
            eventos["delegados"] or
            eventos["presidente"]
        )
        if hay_evento:
            proximos.append({
                "turno":   t,
                "fecha":   turno_a_fecha(t)["texto"],
                "eventos": eventos
            })
        t += 1
    return proximos

# ── Variables secundarias ──
def contar_diputados_por_color(distritos):
    """
    Cuenta cuántos diputados tiene cada color.
    Devuelve un dict {color: cantidad}
    """
    conteo = {c: 0 for c in COLORES}
    for d in distritos:
        diputado = d.get("diputado")
        if diputado:
            # Extraer color del string "Diputado N (Color)"
            color = diputado.split("(")[-1].replace(")", "").strip()
            if color in conteo:
                conteo[color] += 1
    return conteo

def contar_senadores_por_color(provincias):
    """
    Cuenta cuántos senadores tiene cada color.
    Devuelve un dict {color: cantidad}
    """
    conteo = {c: 0 for c in COLORES}
    for p in provincias:
        for cargo in ["senador_A", "senador_B"]:
            valor = p.get(cargo)
            if valor:
                # Extraer color del string "Senador X N (Color)"
                color = valor.split("(")[-1].replace(")", "").strip()
                if color in conteo:
                    conteo[color] += 1
    return conteo
# ══════════════════════════════════════════════
# BLOQUE 4: Umbral de candidaturas y elecciones
# ══════════════════════════════════════════════

# ── Constantes ──
UMBRAL_CANDIDATURA  = 0.15   # 15% mínimo para presentar candidato
VOTOS_PARA_GANAR    = 46     # Votos de delegados necesarios para ganar presidencia
TOTAL_DELEGADOS     = 90     # 3 delegados × 30 provincias

# ── Umbral de candidaturas ──
def obtener_candidatos(ideologia):
    """
    Devuelve la lista de colores que superan el umbral del 15%.
    Aplica para distrito, provincia o país según la ideología entregada.
    """
    return [c for c, proporcion in ideologia.items() if proporcion >= UMBRAL_CANDIDATURA]

# ── Resultado electoral ──
def ordenar_resultado(votos, ideologia):
    """
    Ordena los resultados electorales de mayor a menor.
    Devuelve una lista de dicts con:
      - color
      - votos_proporcion: proporción del total (0.0 a 1.0)
      - votos_porcentaje: porcentaje (0.0 a 100.0)
      - votos_absolutos: cantidad de personas
    La población base se extrae de la ideología del territorio.
    """
    poblacion_base = 1.0  # proporciones ya normalizadas
    resultado = []
    for color, proporcion in votos.items():
        resultado.append({
            "color":             color,
            "votos_proporcion":  proporcion,
            "votos_porcentaje":  round(proporcion * 100, 2),
            "votos_absolutos":   round(proporcion * poblacion_base, 4)
        })
    return sorted(resultado, key=lambda x: x["votos_proporcion"], reverse=True)

# ── Elecciones de distrito ──
def eleccion_distrito(distrito):
    """
    Elección de diputado en un distrito.
    Gana el candidato con mayor porcentaje de votos (mayoría simple).
    Actualiza el campo 'diputado' del distrito.
    Devuelve:
      - resultado: lista ordenada de candidatos con sus votos
      - nulos: proporción de votos nulos
      - ganador: color ganador (o None si no hay candidatos)
    """
    candidatos = obtener_candidatos(distrito["ideologia"])

    if not candidatos:
        distrito["diputado"] = None
        return [], 1.0, None

    votos, nulos = calcular_votos(distrito["ideologia"], candidatos)
    resultado    = ordenar_resultado(votos, distrito["ideologia"])
    ganador      = resultado[0]["color"]

    # Asignar diputado al distrito
    distrito["diputado"] = f"Diputado {distrito['numero']} ({ganador})"

    return resultado, nulos, ganador

# ── Elecciones de provincia (senadores) ──
def eleccion_provincia(provincia):
    """
    Elección de senadores en una provincia.
    Ganan los dos candidatos con mayor porcentaje de votos.
    Actualiza los campos 'senador_A' y 'senador_B' de la provincia.
    Devuelve:
      - resultado: lista ordenada de candidatos con sus votos
      - nulos: proporción de votos nulos
      - senador_A: color del primer electo (o None)
      - senador_B: color del segundo electo (o None)
    """
    candidatos = obtener_candidatos(provincia["ideologia"])

    if not candidatos:
        provincia["senador_A"] = None
        provincia["senador_B"] = None
        return [], 1.0, None, None

    votos, nulos = calcular_votos(provincia["ideologia"], candidatos)
    resultado    = ordenar_resultado(votos, provincia["ideologia"])

    senador_A = resultado[0]["color"] if len(resultado) >= 1 else None
    senador_B = resultado[1]["color"] if len(resultado) >= 2 else None

    # Asignar senadores a la provincia
    provincia["senador_A"] = f"Senador A {provincia['numero']} ({senador_A})"
    provincia["senador_B"] = f"Senador B {provincia['numero']} ({senador_B})"

    return resultado, nulos, senador_A, senador_B

# ── Elección de delegados ──
def eleccion_delegados(provincia):
    """
    Elección de delegados en una provincia.
    NO opera en el turno 1.
    Ganan los tres candidatos con mayor porcentaje de votos.
    Actualiza los campos 'delegado_A', 'delegado_B', 'delegado_C' de la provincia.
    Devuelve:
      - resultado: lista ordenada de candidatos con sus votos
      - nulos: proporción de votos nulos
      - delegado_A, delegado_B, delegado_C: colores electos (o None)
    """
    candidatos = obtener_candidatos(provincia["ideologia"])

    if not candidatos:
        provincia["delegado_A"] = None
        provincia["delegado_B"] = None
        provincia["delegado_C"] = None
        return [], 1.0, None, None, None

    votos, nulos = calcular_votos(provincia["ideologia"], candidatos)
    resultado    = ordenar_resultado(votos, provincia["ideologia"])

    delegado_A = resultado[0]["color"] if len(resultado) >= 1 else None
    delegado_B = resultado[1]["color"] if len(resultado) >= 2 else None
    delegado_C = resultado[2]["color"] if len(resultado) >= 3 else None

    # Asignar delegados a la provincia
    provincia["delegado_A"] = f"Delegado A {provincia['numero']} ({delegado_A})"
    provincia["delegado_B"] = f"Delegado B {provincia['numero']} ({delegado_B})"
    provincia["delegado_C"] = f"Delegado C {provincia['numero']} ({delegado_C})"

    return resultado, nulos, delegado_A, delegado_B, delegado_C

# ── Elecciones de país (presidente) ──
def eleccion_presidente_turno1(colores):
    """
    En el turno 1 el presidente se designa aleatoriamente
    entre todos los colores disponibles.
    Devuelve el color ganador.
    """
    return random.choice(colores)

def eleccion_presidente_delegados(provincias, ideologia_pais):
    """
    Elección presidencial por voto de delegados.
    Cada delegado vota por su propio color si tiene candidato,
    o redistribuye según afinidades si no lo tiene.
    Necesita 46 de 90 votos para ganar.
    Devuelve:
      - ganador: color ganador (o None si nadie alcanza 46)
      - votos_por_candidato: dict {color: cantidad de votos de delegados}
      - resultado: lista ordenada
    """
    candidatos = obtener_candidatos(ideologia_pais)

    if not candidatos:
        return None, {}, []

    # Contar votos de delegados
    votos_delegados = {c: 0 for c in candidatos}

    for p in provincias:
        for cargo in ["delegado_A", "delegado_B", "delegado_C"]:
            delegado = p.get(cargo)
            if delegado is None:
                continue
            # Extraer el color del string "Delegado X N (Color)"
            color_delegado = delegado.split("(")[-1].replace(")", "").strip()

            if color_delegado in candidatos:
                votos_delegados[color_delegado] += 1
            else:
                # Redistribuir por afinidades hacia candidatos disponibles
                afinidades_validas = [
                    a for a in AFINIDADES[color_delegado] if a in candidatos
                ]
                if afinidades_validas:
                    # El delegado vota por su primera afinidad disponible
                    votos_delegados[afinidades_validas[0]] += 1

    resultado = sorted(
        [{"color": c, "votos": v} for c, v in votos_delegados.items()],
        key=lambda x: x["votos"], reverse=True
    )

    ganador = resultado[0]["color"] if resultado[0]["votos"] >= VOTOS_PARA_GANAR else None

    return ganador, votos_delegados, resultado

def eleccion_presidente_provincial(provincias, ideologia_pais):
    """
    Segunda vuelta presidencial por voto provincial.
    Se activa si ningún candidato obtuvo 46 votos de delegados.
    Cada provincia tiene 1 voto, determinado por la mayoría de sus diputados.
    Cada diputado vota por el candidato de mayor afinidad ideológica.
    Gana el candidato con más votos provinciales.
    Devuelve:
      - ganador: color ganador
      - votos_por_candidato: dict {color: cantidad de votos provinciales}
      - resultado: lista ordenada
    """
    candidatos = obtener_candidatos(ideologia_pais)

    if not candidatos:
        return None, {}, []

    votos_provinciales = {c: 0 for c in candidatos}

    for p in provincias:
        # Contar votos de diputados de la provincia hacia candidatos
        votos_diputados = {c: 0 for c in candidatos}

        for d in p["distritos"]:
            diputado = d.get("diputado")
            if diputado is None:
                continue
            # Extraer el color del string "Diputado N (Color)"
            color_diputado = diputado.split("(")[-1].replace(")", "").strip()

            if color_diputado in candidatos:
                votos_diputados[color_diputado] += 1
            else:
                # Votar por primera afinidad disponible entre candidatos
                afinidades_validas = [
                    a for a in AFINIDADES[color_diputado] if a in candidatos
                ]
                if afinidades_validas:
                    votos_diputados[afinidades_validas[0]] += 1

        # La provincia vota por el candidato con más votos de diputados
        if any(v > 0 for v in votos_diputados.values()):
            voto_provincia = max(votos_diputados, key=votos_diputados.get)
            votos_provinciales[voto_provincia] += 1

    resultado = sorted(
        [{"color": c, "votos": v} for c, v in votos_provinciales.items()],
        key=lambda x: x["votos"], reverse=True
    )

    ganador = resultado[0]["color"] if resultado else None

    return ganador, votos_provinciales, resultado
# ══════════════════════════════════════════════
# BLOQUE 5: Integración
# ══════════════════════════════════════════════

def inicializar_juego():
    """
    Construye el estado completo del juego en el Turno 1.
    Ejecuta en orden:
      1. Crea el mundo (distritos, provincias, país)
      2. Asigna ideología a distritos, provincias y país
      3. Asigna clases de senadores aleatoriamente
      4. Realiza las elecciones del Turno 1
      5. Inicializa el tiempo
    Devuelve el estado completo del juego.
    """

    # ── Paso 1: Crear el mundo ──
    distritos, provincias, pais = inicializar_mundo()

    # ── Paso 2: Asignar ideología ──
    distritos = asignar_ideologia_a_distritos(distritos)
    provincias, ideologia_pais = asignar_ideologia_a_provincias_y_pais(provincias)
    pais["ideologia"] = ideologia_pais

    # ── Paso 3: Asignar clases de senadores ──
    provincias = asignar_clases_senadores(provincias)

    # ── Paso 4: Elecciones del Turno 1 ──

    # Elecciones de distrito (diputados)
    resultados_distritos = []
    for d in distritos:
        resultado, nulos, ganador = eleccion_distrito(d)
        resultados_distritos.append({
            "distrito":  d["numero"],
            "ganador":   ganador,
            "resultado": resultado,
            "nulos":     nulos
        })

    # Elecciones de provincia (senadores clase 1 únicamente)
    resultados_provincias = []
    for p in provincias:
        if p["clase_senadores"] == 1:
            resultado, nulos, senA, senB = eleccion_provincia(p)
            resultados_provincias.append({
                "provincia": p["numero"],
                "senador_A": senA,
                "senador_B": senB,
                "resultado": resultado,
                "nulos":     nulos
            })

    # Delegados: no operan en turno 1

    # Presidente: designación aleatoria en turno 1
    presidente_color = eleccion_presidente_turno1(COLORES)
    pais["presidente"] = f"Presidente ({presidente_color})"

    # ── Paso 5: Inicializar tiempo ──
    tiempo = inicializar_tiempo()

    # ── Paso 6: Variables secundarias ──
    conteo_diputados  = contar_diputados_por_color(distritos)
    conteo_senadores  = contar_senadores_por_color(provincias)

    # ── Estado completo del juego ──
    return {
        "tiempo":               tiempo,
        "distritos":            distritos,
        "provincias":           provincias,
        "pais":                 pais,
        "conteo_diputados":     conteo_diputados,
        "conteo_senadores":     conteo_senadores,
        "resultados_distritos": resultados_distritos,
        "resultados_provincias":resultados_provincias,
        "pendiente_segunda_vuelta": False,
        "log": [
            f"Turno 1 — {turno_a_fecha(1)['texto']}: Juego inicializado.",
            f"Presidente designado aleatoriamente: {presidente_color}."
        ]
    }

def avanzar_turno(estado):
    """
    Avanza el juego un turno.
    Verifica el calendario electoral y ejecuta
    las elecciones que correspondan.
    Devuelve el estado actualizado.
    """
    # Avanzar tiempo
    estado["tiempo"] = avanzar_tiempo(estado["tiempo"])
    turno            = estado["tiempo"]["turno"]
    fecha            = turno_a_fecha(turno)["texto"]
    log_turno        = [f"Turno {turno} — {fecha}"]

    distritos  = estado["distritos"]
    provincias = estado["provincias"]
    pais       = estado["pais"]

    # Verificar segunda vuelta presidencial pendiente
    if estado.get("pendiente_segunda_vuelta"):
        ganador, votos, resultado = eleccion_presidente_provincial(provincias, pais["ideologia"])
        pais["presidente"] = f"Presidente ({ganador})"
        estado["pendiente_segunda_vuelta"] = False
        log_turno.append(f"Segunda vuelta presidencial: ganador {ganador}.")

    # Consultar calendario electoral
    eventos = elecciones_en_turno(turno, provincias)

    # ── Elecciones de diputados ──
    if eventos["diputados"]:
        resultados_distritos = []
        for d in distritos:
            resultado, nulos, ganador = eleccion_distrito(d)
            resultados_distritos.append({
                "distrito":  d["numero"],
                "ganador":   ganador,
                "resultado": resultado,
                "nulos":     nulos
            })
        estado["resultados_distritos"] = resultados_distritos
        estado["conteo_diputados"]     = contar_diputados_por_color(distritos)
        log_turno.append("Elecciones de Diputados realizadas.")

    # ── Elecciones de senadores ──
    if eventos["senadores"]:
        resultados_provincias = []
        for p in provincias:
            if p["numero"] in eventos["senadores"]:
                resultado, nulos, senA, senB = eleccion_provincia(p)
                resultados_provincias.append({
                    "provincia": p["numero"],
                    "senador_A": senA,
                    "senador_B": senB,
                    "resultado": resultado,
                    "nulos":     nulos
                })
        estado["resultados_provincias"] = resultados_provincias
        estado["conteo_senadores"]      = contar_senadores_por_color(provincias)
        log_turno.append("Elecciones de Senadores realizadas.")

    # ── Elecciones de delegados ──
    if eventos["delegados"]:
        for p in provincias:
            eleccion_delegados(p)
        log_turno.append("Elecciones de Delegados realizadas.")

    # ── Elecciones de presidente ──
    if eventos["presidente"]:
        ganador, votos, resultado = eleccion_presidente_delegados(provincias, pais["ideologia"])
        if ganador:
            pais["presidente"] = f"Presidente ({ganador})"
            log_turno.append(f"Elección presidencial: ganador {ganador}.")
        else:
            estado["pendiente_segunda_vuelta"] = True
            log_turno.append("Elección presidencial: ningún candidato alcanzó 46 votos. Segunda vuelta el próximo turno.")

    estado["log"] = estado["log"] + log_turno
    return estado
