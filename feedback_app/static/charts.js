const graficoNotasDados = JSON.parse('{{ grafico_notas | safe }}');
const ctxNotas = document.getElementById('graficoNotas').getContext('2d');

new Chart(ctxNotas, {
    type: 'bar',
    data: {
        labels: ['Nota 1', 'Nota 2', 'Nota 3', 'Nota 4', 'Nota 5'],
        datasets: [{
            label: 'Quantidade de Notas',
            data: graficoNotasDados,
            backgroundColor: ['#FF5C5C', '#FFA500', '#FFD700', '#32CD32', '#2E8B57']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: true },
            title: { display: true, text: 'Distribuição de Notas' }
        }
    }
});
