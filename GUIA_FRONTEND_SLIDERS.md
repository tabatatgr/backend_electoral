# 🎛️ Guía: Conectar Backend ↔ Frontend para Sliders Inteligentes

## 🏗️ **Arquitectura de la Solución**

```
Frontend (JavaScript)     ←→     Backend (Python)
├─ Sliders automáticos           ├─ Validaciones robustas  
├─ Validación en tiempo real     ├─ Auto-corrección
├─ UI responsiva                 ├─ Logs informativos
└─ UX fluida                     └─ Cálculos electorales
```

## 🎯 **Estrategia de Implementación**

### 📱 **FRONTEND (JavaScript/React/Vue)**
- **Sliders que se mueven automáticamente**
- **Validación en tiempo real**
- **Feedback visual al usuario**

### 🖥️ **BACKEND (Python FastAPI)**  
- **Validación robusta final**
- **Auto-corrección de valores**
- **Cálculos electorales**

---

## 💻 **Código Frontend Ejemplo (React/JavaScript)**

### 🎛️ **Componente de Sliders Inteligentes**

```jsx
import React, { useState, useEffect } from 'react';

function SlidersInteligentes({ magnitudTotal = 119 }) {
    const [mrSeats, setMrSeats] = useState(60);
    const [rpSeats, setRpSeats] = useState(59);
    const [ultimoModificado, setUltimoModificado] = useState('mr');

    // 🎛️ SLIDERS AUTOMÁTICOS - Cuando cambia MR, ajustar RP
    const handleMrChange = (nuevoMr) => {
        const nuevoMrNum = parseInt(nuevoMr);
        const minMr = Math.max(1, Math.floor(magnitudTotal * 0.1)); // 10% mínimo
        const maxMr = magnitudTotal - Math.max(1, Math.floor(magnitudTotal * 0.1)); // 90% máximo
        
        // Aplicar límites
        const mrLimitado = Math.min(Math.max(nuevoMrNum, minMr), maxMr);
        
        // Auto-ajustar RP
        const nuevoRp = magnitudTotal - mrLimitado;
        
        setMrSeats(mrLimitado);
        setRpSeats(nuevoRp);
        setUltimoModificado('mr');
        
        console.log(`🎛️ Slider MR: ${nuevoMrNum} → ${mrLimitado}, RP auto-ajustado: ${nuevoRp}`);
    };

    // 🎛️ SLIDERS AUTOMÁTICOS - Cuando cambia RP, ajustar MR  
    const handleRpChange = (nuevoRp) => {
        const nuevoRpNum = parseInt(nuevoRp);
        const minRp = Math.max(1, Math.floor(magnitudTotal * 0.1)); // 10% mínimo
        const maxRp = magnitudTotal - Math.max(1, Math.floor(magnitudTotal * 0.1)); // 90% máximo
        
        // Aplicar límites
        const rpLimitado = Math.min(Math.max(nuevoRpNum, minRp), maxRp);
        
        // Auto-ajustar MR
        const nuevoMr = magnitudTotal - rpLimitado;
        
        setRpSeats(rpLimitado);
        setMrSeats(nuevoMr);
        setUltimoModificado('rp');
        
        console.log(`🎛️ Slider RP: ${nuevoRpNum} → ${rpLimitado}, MR auto-ajustado: ${nuevoMr}`);
    };

    // ✅ Validación visual en tiempo real
    const sumaTotal = mrSeats + rpSeats;
    const esValido = sumaTotal === magnitudTotal;

    return (
        <div className="sliders-container">
            <h3>Distribución de Escaños (Total: {magnitudTotal})</h3>
            
            {/* Slider MR */}
            <div className="slider-group">
                <label>Mayoría Relativa (MR): {mrSeats}</label>
                <input
                    type="range"
                    min={Math.max(1, Math.floor(magnitudTotal * 0.1))}
                    max={magnitudTotal - Math.max(1, Math.floor(magnitudTotal * 0.1))}
                    value={mrSeats}
                    onChange={(e) => handleMrChange(e.target.value)}
                    className={ultimoModificado === 'mr' ? 'slider-active' : 'slider-auto'}
                />
            </div>

            {/* Slider RP */}
            <div className="slider-group">
                <label>Representación Proporcional (RP): {rpSeats}</label>
                <input
                    type="range"
                    min={Math.max(1, Math.floor(magnitudTotal * 0.1))}
                    max={magnitudTotal - Math.max(1, Math.floor(magnitudTotal * 0.1))}
                    value={rpSeats}
                    onChange={(e) => handleRpChange(e.target.value)}
                    className={ultimoModificado === 'rp' ? 'slider-active' : 'slider-auto'}
                />
            </div>

            {/* Indicador de validación */}
            <div className={`validation-indicator ${esValido ? 'valid' : 'invalid'}`}>
                {esValido ? (
                    <span>✅ Suma correcta: {sumaTotal} = {magnitudTotal}</span>
                ) : (
                    <span>❌ Suma incorrecta: {sumaTotal} ≠ {magnitudTotal}</span>
                )}
            </div>
        </div>
    );
}

export default SlidersInteligentes;
```

### 🎨 **CSS para Feedback Visual**

```css
.sliders-container {
    padding: 20px;
    border-radius: 8px;
    background: #f5f5f5;
}

.slider-group {
    margin-bottom: 15px;
}

.slider-active {
    background: #007bff;  /* Azul - slider que el usuario está moviendo */
}

.slider-auto {
    background: #28a745;  /* Verde - slider que se ajusta automáticamente */
}

.validation-indicator.valid {
    color: #28a745;
    font-weight: bold;
}

.validation-indicator.invalid {
    color: #dc3545;
    font-weight: bold;
}
```

---

## 🔗 **Conectar con Backend**

### 📡 **Función para enviar al backend**

```javascript
async function enviarConfiguracion(mrSeats, rpSeats, magnitudTotal) {
    try {
        const response = await fetch('/diputados', {
            method: 'GET',
            url: `http://localhost:8001/diputados?anio=2021&modelo=personalizado&sistema=mixto&mixto_mr_seats=${mrSeats}&mixto_rp_seats=${rpSeats}&magnitud=${magnitudTotal}`
        });
        
        const resultado = await response.json();
        console.log('📊 Resultado del backend:', resultado);
        return resultado;
        
    } catch (error) {
        console.error('❌ Error conectando con backend:', error);
    }
}
```

---

## 🎯 **Flujo Completo**

1. **👤 Usuario mueve slider MR a 80**
2. **🎛️ Frontend auto-ajusta RP a 39** (119-80=39)
3. **✅ Validación visual en tiempo real**
4. **📡 Envío al backend:** `mixto_mr_seats=80&mixto_rp_seats=39`
5. **🛡️ Backend valida** (si es necesario, ajusta)
6. **🔢 Backend calcula** resultados electorales
7. **📊 Frontend muestra** resultados finales

---

## 🚀 **Ventajas de esta Arquitectura**

- **🎛️ UX fluida:** Sliders se mueven inmediatamente
- **✅ Validación doble:** Frontend (UX) + Backend (seguridad)
- **🛡️ Robustez:** Backend siempre valida como respaldo
- **📱 Responsivo:** Funciona en tiempo real
- **🎯 Intuitivo:** Usuario ve inmediatamente el efecto

¿Te sirve este enfoque? ¿En qué framework tienes el frontend?
