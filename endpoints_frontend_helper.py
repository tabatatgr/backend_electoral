#!/usr/bin/env python3
# 🔧 Endpoint adicional para el frontend: obtener rangos válidos

# Agregar esto al main.py para ayudar al frontend

@app.get("/validacion-rangos")
async def obtener_rangos_validacion(
    magnitud: int = Query(119, description="Número total de escaños"),
    sistema: str = Query("mixto", description="Sistema electoral")
):
    """
    🎛️ Endpoint para que el frontend obtenga los rangos válidos para los sliders
    
    Esto permite que el frontend configure los sliders con los límites correctos
    """
    
    try:
        # Calcular rangos según la magnitud
        min_percent = 0.1  # 10% mínimo
        max_percent = 0.9  # 90% máximo
        
        min_seats = max(1, int(magnitud * min_percent))
        max_seats = magnitud - min_seats
        
        rangos = {
            "magnitud_total": magnitud,
            "sistema": sistema,
            "mr_seats": {
                "min": min_seats,
                "max": max_seats,
                "default": magnitud // 2 if sistema == "mixto" else magnitud
            },
            "rp_seats": {
                "min": min_seats,  
                "max": max_seats,
                "default": magnitud // 2 if sistema == "mixto" else 0
            },
            "validaciones": {
                "suma_debe_ser_exacta": magnitud,
                "min_porcentaje": f"{min_percent*100}%",
                "max_porcentaje": f"{max_percent*100}%"
            }
        }
        
        return {
            "status": "success",
            "rangos": rangos,
            "mensaje": f"Rangos válidos para {magnitud} escaños en sistema {sistema}"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "mensaje": "Error calculando rangos de validación"
        }


@app.get("/validar-configuracion")
async def validar_configuracion(
    magnitud: int = Query(119),
    mixto_mr_seats: int = Query(None),
    mixto_rp_seats: int = Query(None)
):
    """
    🛡️ Endpoint para validar una configuración antes de calcular
    
    El frontend puede usar esto para mostrar warnings en tiempo real
    """
    
    try:
        max_seats = magnitud
        warnings = []
        ajustes = {}
        
        # Simular las mismas validaciones del endpoint principal
        mr_original = mixto_mr_seats
        rp_original = mixto_rp_seats
        
        # === VALIDACIONES ===
        if mixto_mr_seats is not None and mixto_rp_seats is not None:
            suma = mixto_mr_seats + mixto_rp_seats
            if suma != max_seats:
                warnings.append(f"Suma incorrecta: {suma} ≠ {max_seats}")
                ajustes["rp_ajustado"] = max_seats - mixto_mr_seats
                
        elif mixto_mr_seats is not None and mixto_rp_seats is None:
            ajustes["rp_calculado"] = max_seats - mixto_mr_seats
            
        elif mixto_rp_seats is not None and mixto_mr_seats is None:
            ajustes["mr_calculado"] = max_seats - mixto_rp_seats
        
        # Validar rangos
        min_val = max(1, max_seats // 10)
        max_val = max_seats - min_val
        
        if mixto_mr_seats and (mixto_mr_seats < min_val or mixto_mr_seats > max_val):
            warnings.append(f"MR fuera de rango ({min_val}-{max_val})")
            
        if mixto_rp_seats and (mixto_rp_seats < min_val or mixto_rp_seats > max_val):
            warnings.append(f"RP fuera de rango ({min_val}-{max_val})")
        
        return {
            "status": "success",
            "valido": len(warnings) == 0,
            "warnings": warnings,
            "ajustes_sugeridos": ajustes,
            "configuracion_original": {
                "mr": mr_original,
                "rp": rp_original
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# 📡 Ejemplo de uso desde el frontend:

"""
JavaScript para el frontend:

// 1. Obtener rangos válidos al cargar la página
async function obtenerRangos(magnitud) {
    const response = await fetch(`/validacion-rangos?magnitud=${magnitud}`);
    const data = await response.json();
    
    // Configurar sliders con los rangos obtenidos
    configurarSliders(data.rangos);
}

// 2. Validar configuración en tiempo real
async function validarEnTiempoReal(mr, rp, magnitud) {
    const response = await fetch(`/validar-configuracion?magnitud=${magnitud}&mixto_mr_seats=${mr}&mixto_rp_seats=${rp}`);
    const data = await response.json();
    
    // Mostrar warnings al usuario
    mostrarWarnings(data.warnings);
    
    // Aplicar ajustes sugeridos
    if (data.ajustes_sugeridos) {
        aplicarAjustes(data.ajustes_sugeridos);
    }
}
"""
