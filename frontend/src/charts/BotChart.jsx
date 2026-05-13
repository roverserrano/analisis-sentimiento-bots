import { Bar } from 'react-chartjs-2'

const BOT_LABELS = ['No bot', 'Bot']
const BOT_COLORS = ['#10b981', '#8b5cf6']

function BotChart({ data, title = 'Bot vs No bot' }) {
  const values = BOT_LABELS.map((label) => data?.[label] || 0)

  return (
    <div className="chart-card">
      <h3>{title}</h3>
      <Bar
        data={{
          labels: BOT_LABELS,
          datasets: [
            {
              label: 'Comentarios',
              data: values,
              backgroundColor: BOT_COLORS,
              borderWidth: 0,
              borderRadius: 8,
            },
          ],
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: { color: '#7c8db5' },
              grid: { color: '#1f2e4d' },
            },
            y: {
              beginAtZero: true,
              ticks: { color: '#7c8db5', precision: 0 },
              grid: { color: '#1f2e4d' },
            },
          },
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#0f1629', borderColor: '#1f2e4d', borderWidth: 1 },
          },
        }}
      />
    </div>
  )
}

export default BotChart

