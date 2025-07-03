
document.addEventListener("DOMContentLoaded", () => {
    const sections = [
        'home-content',
        'section-1',
        'section-2',
        'section-3',
        'section-4',
        'section-5'
    ];

    document.querySelectorAll('.nav li').forEach((item, index) => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav li').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
            sections.forEach((id, i) => {
                document.getElementById(id).style.display = i === index ? 'block' : 'none';
            });
        });
    });

    sections.forEach((id, i) => {
        document.getElementById(id).style.display = i === 0 ? 'block' : 'none';
    });

});


//Grafico de estados
let chart;

async function cargarGraficoEstados(filtro = null) {
    const colores = [
        '#4dc9f6', '#f67019', '#f53794', '#537bc4', '#acc236',
        '#166a8f', '#00a950', '#58595b', '#8549ba', '#e6c229'
    ];

    const res = await fetch('../data_limpios/state_chart.json');
    const data = await res.json();
    const estados = data.labels.map((label, i) => ({ label, value: data.values[i] }));

    const sorted = estados.sort((a, b) => b.value - a.value);
    const top10 = filtro ? estados.filter(d => d.label === filtro) : sorted.slice(0, 10);

    const labels = top10.map(d => d.label);
    const values = top10.map(d => d.value);

    const ctx = document.getElementById('stateChart').getContext('2d');
    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad de videos',
                data: values,
                backgroundColor: colores.slice(0, values.length),
                borderRadius: 6
            }]
        },
        options: {
            responsive: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#ccc' },
                    grid: { color: '#333' }
                },
                x: {
                    ticks: { display: false },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.raw} videos`
                    }
                },
                datalabels: {
                    anchor: 'center',
                    align: 'center',
                    color: '#fff',
                    font: {
                        weight: 'bold',
                        size: 12
                    },
                    rotation: -90,
                    formatter: (value, ctx) => ctx.chart.data.labels[ctx.dataIndex]
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}

document.getElementById('downloadChart').addEventListener('click', () => {
    const link = document.createElement('a');
    link.href = chart.toBase64Image();
    link.download = 'estado_chart.png';
    link.click();
});

async function cargarSelectorEstados() {
    const res = await fetch('../data_limpios/state_chart.json');
    const data = await res.json();
    const selector = document.getElementById('estadoSelector');
    const opciones = data.labels;

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Top 10 Estados';
    selector.appendChild(defaultOption);

    opciones.forEach(estado => {
        const opt = document.createElement('option');
        opt.value = estado;
        opt.textContent = estado;
        selector.appendChild(opt);
    });

    selector.addEventListener('change', e => {
        const filtro = e.target.value;
        cargarGraficoEstados(filtro || null);
    });
}

cargarGraficoEstados();
cargarSelectorEstados();



fetch('../data_limpios/dtype_distribution.json')
    .then(res => res.json())
    .then(data => {
        const ctx = document.getElementById('dtypePieChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        '#4bc0c0', '#ff6384', '#ffce56', '#36a2eb',
                        '#9966ff', '#ff9f40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        align: 'center',
                        labels: { color: '#ccc' }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.label}: ${ctx.raw} columnas`
                        }
                    }
                }
            }
        });
    })
    .catch(err => console.error('Error cargando distribución de dtypes:', err));

fetch('../data_limpios/freq_cat.json')
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById('freq-table');
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';

        const thead = document.createElement('thead');
        thead.innerHTML = `
        <tr>
          <th style="text-align:left; padding:8px; border-bottom:1px solid #444;">Categoría</th>
          <th style="text-align:right; padding:8px; border-bottom:1px solid #444;">Cantidad</th>
        </tr>`;
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        data.categories.forEach((cat, i) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
          <td style="padding:6px 8px; border-bottom:1px solid #333;">${cat}</td>
          <td style="padding:6px 8px; text-align:right; border-bottom:1px solid #333;">
            ${data.counts[i].toLocaleString()}
          </td>`;
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        container.appendChild(table);
    })
    .catch(err => {
        console.error('Error cargando tabla de frecuencia:', err);
        document.getElementById('freq-table').textContent = 'No se pudo cargar la tabla.';
    });

document.getElementById('filter-btn').addEventListener('click', () => {
    const input = document.getElementById('freq-filter');
    input.style.display = input.style.display === 'none' ? 'block' : 'none';
    if (input.style.display === 'block') input.focus();
});
document.getElementById('freq-filter').addEventListener('input', e => {
    const term = e.target.value.toLowerCase();
    document.querySelectorAll('#freq-table tbody tr').forEach(row => {
        const cat = row.children[0].textContent.toLowerCase();
        row.style.display = cat.includes(term) ? '' : 'none';
    });
});

document.getElementById('download-btn').addEventListener('click', () => {
    fetch('../data_limpios/freq_cat.json')
        .then(res => res.json())
        .then(data => {
            const lines = [['Categoría', 'Cantidad']];
            data.categories.forEach((cat, i) => lines.push([cat, data.counts[i]]));
            const csv = lines.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'freq_cat.csv';
            a.click();
        });
});

(async function () {
    try {
        const resp = await fetch('../data_limpios/stats.json');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const stats = await resp.json();

        document.getElementById('stat-rows').textContent =
            stats.total_rows.toLocaleString();

        const likesEl = document.getElementById('stat-likes');
        const iconEl = document.getElementById('reactions-icon');
        const labelEl = document.querySelector('#reactions-card .hc-label');
        let showingLike = true;
        likesEl.textContent = stats.total_likes.toLocaleString();
        labelEl.textContent = 'Likes';

        setInterval(() => {
            if (showingLike) {
                iconEl.textContent = '👎';
                likesEl.textContent = stats.total_dislikes.toLocaleString();
                labelEl.textContent = 'Dislikes';
            } else {
                iconEl.textContent = '👍';
                likesEl.textContent = stats.total_likes.toLocaleString();
                labelEl.textContent = 'Likes';
            }
            showingLike = !showingLike;
        }, 5000);

        document.getElementById('stat-views').textContent =
            stats.total_views.toLocaleString();

        document.getElementById('stat-comments').textContent =
            stats.total_comments.toLocaleString();

    } catch (err) {
        console.error('No se pudieron cargar las estadísticas:', err);
    }
})();

// Cargar gráfico de publicaciones por año
let pubChart;
fetch("../data_limpios/pub_years.json")
    .then(res => res.json())
    .then(data => {
        const ctx = document.getElementById("pubChart").getContext("2d");
        pubChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: "Videos publicados",
                        data: data.values,
                        borderColor: "#a88beb",
                        borderWidth: 3,
                        tension: 0.4,
                        pointRadius: 0,
                        fill: false
                    },
                    {
                        label: "Promedio de vistas",
                        data: data.avg_views,
                        borderColor: "#36a2eb",
                        borderWidth: 2,
                        tension: 0.3,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: "#ccc" }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.dataset.label}: ${ctx.raw.toLocaleString()}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: "#ccc" },
                        grid: { color: "#333" }
                    },
                    x: {
                        ticks: { color: "#ccc" },
                        grid: { display: false }
                    }
                }
            }
        });
    });

document.getElementById("downloadPubChart").addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = pubChart.toBase64Image();
    link.download = "publicaciones_por_anio.png";
    link.click();
});
const sel = document.getElementById("timeframe");
const img = document.getElementById("chartImage");
const tbody = document.querySelector('#dataTable tbody');
const downloadBtn = document.getElementById("downloadDataBtn");
const pieCtx = document.getElementById("downloadsChart").getContext("2d");

const columnsMap = {
    '1': ['category_name'],
    '2': ['category_name', 'likes'],
    '3': ['category_name', 'likes', 'dislikes'],
    '4': ['category_name', 'views', 'comment_count'],
    '5': ['trending_date_dt'],
    '6a': ['channel_title'],
    '6b': ['channel_title'],
    '7': ['state', 'views', 'likes', 'dislikes', 'lat', 'lon'],
    '8': ['title', 'comment_count'],
    '9': ['views', 'likes', 'dislikes', 'comment_count']
};

function updateDataTable(key) {
    const cols = columnsMap[key] || [];
    tbody.innerHTML = '';
    cols.forEach(col => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td style="border:1px solid #555; padding:8px;">${col}</td>`;
        tbody.appendChild(tr);
    });
}

let pieChart;
function updatePieChart(key) {
    const cols = columnsMap[key] || [];
    const data = cols.map(() => 1);
    const colors = ['#4bc0c0', '#ff6384', '#ffce56', '#36a2eb', '#9966ff', '#ff9f40'];

    if (pieChart) pieChart.destroy();
    pieChart = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: cols,
            datasets: [{ data, backgroundColor: colors.slice(0, cols.length) }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#ccc' } } }
        }
    });
}

sel.addEventListener("change", () => {
    const val = sel.value;
    img.src = `/Programa/static/images/p${val}.png`;
    img.alt = `Gráfico Pregunta ${val}`;
    updateDataTable(val);
    updatePieChart(val);
});

downloadBtn.addEventListener("click", () => {
    const cols = columnsMap[sel.value] || [];
    const csv = "Columna\n" + cols.join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `pregunta_${sel.value}_datos.csv`;
    a.click();
});

img.src = `/Programa/static/images/p${sel.value}.png`;
img.alt = `Gráfico Pregunta ${sel.value}`;
updateDataTable(sel.value);
updatePieChart(sel.value);

fetch('../data_limpios/EEUU_limpio.csv')
    .then(res => res.text())
    .then(text => {
        const lines = text.split('\n').filter(l => l.trim());
        const headers = lines[0].split(',');
        const container = document.getElementById('csvTableContainer');

        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.fontSize = '12px';
        table.style.color = '#fff';

        const thead = document.createElement('thead');
        const headRow = document.createElement('tr');
        headers.forEach(h => {
            const th = document.createElement('th');
            th.textContent = h;
            th.style.padding = '6px';
            th.style.borderBottom = '1px solid #444';
            th.style.background = '#2b2b3d';
            th.style.position = 'sticky';
            th.style.top = '0';
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        lines.slice(1, 6).forEach(line => {
            const tr = document.createElement('tr');
            line.split(',').forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                td.style.padding = '4px';
                td.style.borderBottom = '1px solid #333';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        container.appendChild(table);
    })
    .catch(err => {
        document.getElementById('csvTableContainer')
            .textContent = 'No se pudo cargar el CSV.';
        console.error(err);
    });

fetch('../data/US_category_id.json')
  .then(res => {
    if (!res.ok) throw new Error(`Error HTTP ${res.status}`);
    return res.json();
  })
  .then(data => {
    const pretty = JSON.stringify(data, null, 2);
    const pre = document.getElementById('jsonContainer');
    pre.textContent = pretty;
  })
  .catch(err => {
    const pre = document.getElementById('jsonContainer');
    pre.textContent = '❌ No se pudo cargar el JSON.';
    console.error(err);
  });
