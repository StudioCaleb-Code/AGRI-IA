let elegidasModal = new Set();
let plantasFinales = new Set();
let fertSeleccionado = "organico"; // Por defecto en minúsculas para el modelo

function toggleModal(show) {
    document.getElementById('modal').classList.toggle('active', show);
    if (show) {
        elegidasModal.clear();
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('selected'));
    }
}

function selectPlant(el, name) {
    if (elegidasModal.has(name)) {
        elegidasModal.delete(name);
        el.classList.remove('selected');
    } else {
        elegidasModal.add(name);
        el.classList.add('selected');
    }
}

function confirmarPlantas() {
    elegidasModal.forEach(p => plantasFinales.add(p));
    actualizarListaIzquierda();
    toggleModal(false);
}

function actualizarListaIzquierda() {
    const container = document.getElementById('listaFinal');
    container.innerHTML = "";
    plantasFinales.forEach(p => {
        const div = document.createElement('div');
        div.className = 'planta-item';
        div.innerHTML = `<span>${p}</span><i class="bi bi-trash3" style="color:#ff4757; cursor:pointer;" onclick="borrar('${p}')"></i>`;
        container.appendChild(div);
    });
}

function borrar(name) {
    plantasFinales.delete(name);
    actualizarListaIzquierda();
}

function setFert(el, tipo) {
    document.querySelectorAll('.fert-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    // Convertimos a minúsculas y quitamos tildes para que coincida con el CSV (organico/sintetico)
    fertSeleccionado = tipo.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    if(fertSeleccionado === "inorganico") fertSeleccionado = "sintetico"; // Ajuste según tu fragmento de CSV
}

// --- CONEXIÓN REAL CON EL MODELO PYTHON ---
async function calcular() {
    const container = document.getElementById('contenedorResultados');
    
    if (plantasFinales.size === 0) return alert("Selecciona al menos un cultivo");

    // Mostrar estado de carga
    container.innerHTML = `<div style="text-align:center; padding:20px; color:white;">Analizando con IA...</div>`;

    // Preparar objeto de datos
    const dataToSend = {
        plantas: Array.from(plantasFinales),
        temperatura: document.getElementById('temp').value,
        humedad: document.getElementById('hum').value,
        ph: document.getElementById('ph').value,
        fertilizante: fertSeleccionado
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataToSend)
        });

        const res = await response.json();

        if (res.status === 'success') {
            renderizarResultados(res);
        } else {
            alert("Error en el servidor: " + res.message);
        }
    } catch (error) {
        console.error("Error al conectar con Flask:", error);
        alert("No se pudo conectar con el servidor de IA.");
    }
}

function renderizarResultados(res) {
    const container = document.getElementById('contenedorResultados');
    container.innerHTML = "";

    res.detalles.forEach(item => {
        const pct = item.probabilidad;
        const crecera = item.crecera === "SÍ";

        const row = document.createElement('div');
        row.className = 'planta-resultado-card';
        row.innerHTML = `
            <div class="planta-name">${item.planta}</div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:0.85rem; font-weight:700; width:45px;">${pct}%</span>
                <div class="progress-container">
                    <div class="progress-bar" id="bar-${item.planta}" style="width: 0%; background: ${crecera ? '#15d163' : '#ff4757'}"></div>
                </div>
            </div>
            <div class="status-badge ${crecera ? 'status-si' : 'status-no'}">
                ${crecera ? 'CRECERÁ (SÍ)' : 'BAJO ÉXITO'}
            </div>
        `;
        container.appendChild(row);

        // Animación de la barra con el porcentaje real de la IA
        setTimeout(() => {
            const bar = document.getElementById(`bar-${item.planta}`);
            if(bar) bar.style.width = pct + "%";
        }, 100);
    });

    // Actualizar círculo general
    const promedio = res.promedio;
    document.getElementById('scoreGral').innerText = promedio + "%";
    document.getElementById('scoreGral').style.background = `radial-gradient(closest-side, white 79%, transparent 80% 100%), conic-gradient(#15d163 ${promedio}%, #f0f0f0 0)`;
}

// Cerrar modal al tocar fuera
window.onclick = (e) => { if (e.target == document.getElementById('modal')) toggleModal(false); }