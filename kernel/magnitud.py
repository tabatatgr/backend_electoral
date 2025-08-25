"""
Módulo de magnitud de cámara para el tablero electoral.
Permite definir y devolver la magnitud (número de escaños) de la cámara según parámetros.
"""

def get_magnitud(camara: str, modelo: str = "Vigente") -> int:
    """
    Devuelve la magnitud (número de escaños) para la cámara y modelo especificados.
    Por defecto usa los valores estándar, pero puede adaptarse a modelos alternativos.
    """
    camara = camara.lower()
    modelo = modelo.lower()
    if camara == "diputados":
        if modelo == "vigente":
            return 500
        elif modelo in ("plan a", "plan c"):
            return 300
        else:
            return 500  # fallback
    elif camara == "senado":
        return 128
    else:
        raise ValueError(f"Cámara desconocida: {camara}")
