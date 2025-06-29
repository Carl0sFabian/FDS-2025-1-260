function mostrarOpcionesBaseDatos() {
    document.getElementById("contenido").innerHTML = `
    <h2>Base de Datos</h2>
    <button onclick="mostrarCSV()">Ver CSV</button>
    <button onclick="mostrarJSON()">Ver JSON</button>
    <div id="visor-datos"></div>
`;

}

function mostrarCSV() {
    fetch('../data_limpios/EEUU_limpio.csv')
        .then(response => response.text())
        .then(csvData => {
            const resultados = Papa.parse(csvData, {
                header: true,
                skipEmptyLines: true
            });

            const columnas = Object.keys(resultados.data[0]);
            let html = '<table id="tablaCSV" class="display nowrap" style="width:100%"><thead><tr>';

            columnas.forEach(col => {
                html += `<th>${col}</th>`;
            });

            html += '</tr></thead><tbody>';

            resultados.data.slice(0, 10).forEach(fila => {
                html += '<tr>';
                columnas.forEach(col => {
                    html += `<td>${fila[col]}</td>`;
                });
                html += '</tr>';
            });

            html += '</tbody></table>';
            document.getElementById("visor-datos").innerHTML = html;

            $('#tablaCSV').DataTable({
                scrollX: true,
                pageLength: 20,
                dom: 'Bfrtip',
                buttons: [
                    'copyHtml5',
                    'excelHtml5',
                    'csvHtml5',
                    'print'
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
                }
            });


        });
}


function mostrarJSON() {
    fetch('../data/US_category_id.json')

        .then(response => response.json())
        .then(data => {
            let html = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            document.getElementById("visor-datos").innerHTML = html;
        });
}
