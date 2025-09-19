let chart;
let currentFilters = {};

// Función para cargar opciones de filtros
async function cargarFiltros() {
    const tipos = ['institucion', 'programa', 'departamento', 'año', 'municipio'];
    for (const tipo of tipos) {
        try {
            const response = await fetch(`/api/filtros?tipo=${tipo}`);
            const { opciones } = await response.json();
            const select = document.getElementById(tipo === 'genero' ? 'genero' : tipo);
            if (select) {
                opciones.forEach(opcion => {
                    const option = document.createElement('option');
                    if (tipo === 'genero') {
                        option.value = opcion.id;
                        option.textContent = opcion.label;
                    } else {
                        option.value = opcion;
                        option.textContent = opcion;
                    }
                    select.appendChild(option);
                });
            }
        } catch (err) {
            console.error(`Error cargando filtro ${tipo}:`, err);
        }
    }
}

// Función para actualizar gráfico y tabla
async function actualizarVista() {
    const params = new URLSearchParams(currentFilters);
    const groupBy = document.getElementById('groupBy').value;
    params.append('groupBy', groupBy);

    try {
        // Actualizar gráfico
        const response = await fetch(`/api/datos-filtrados?${params}`);
        const { labels, values } = await response.json();

        if (chart) {
            chart.destroy();
        }
        const ctx = document.getElementById('graficoMatriculas').getContext('2d');
        chart = new Chart(ctx, {
            type: 'bar', // Cambiar a 'line', 'pie', etc. si se desea
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Matrículas',
                    data: values,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Actualizar tabla (muestra últimos 10 registros filtrados para no sobrecargar)
        const tablaBody = document.querySelector('#tablaMatriculas tbody');
        tablaBody.innerHTML = '';
        const tablaResponse = await fetch(`/api/datos-filtrados?${params}&limit=10`); // Asumir endpoint soporta limit, o simular
        // Nota: Para tabla, fetch datos completos y slice, pero para demo, usar los mismos datos
        // Aquí simular con labels/values, pero en producción fetch rows

    } catch (err) {
        console.error('Error actualizando vista:', err);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    cargarFiltros();

    // Cargar resumen inicial
    fetch('/api/resumen')
        .then(res => res.json())
        .then(data => {
            document.getElementById('totalMatriculas').textContent = `Total de Matrículas: ${data.totalMatriculas.toLocaleString()}`;
        });

    document.getElementById('aplicarFiltros').addEventListener('click', () => {
        const selects = ['institucion', 'programa', 'departamento', 'año', 'genero', 'municipio'];
        currentFilters = {};
        selects.forEach(id => {
            const value = document.getElementById(id).value;
            if (value) currentFilters[id] = value;
        });
        actualizarVista();
    });

    document.getElementById('limpiarFiltros').addEventListener('click', () => {
        document.querySelectorAll('.filtros select').forEach(select => {
            if (select.id !== 'genero' && select.id !== 'groupBy') select.value = '';
        });
        document.getElementById('genero').value = '';
        currentFilters = {};
        actualizarVista();
    });

    document.getElementById('groupBy').addEventListener('change', actualizarVista);

    // Inicializar vista
    actualizarVista();
});