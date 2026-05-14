import { Doughnut } from 'react-chartjs-2'

const SENTIMENT_COLORS = ['#10b981', '#f59e0b', '#ef4444']
const SENTIMENT_LABELS = ['Bueno', 'Regular', 'Malo']

function SentimentChart({ data, title = 'Distribucion de sentimientos' }) {
  const values = SENTIMENT_LABELS.map((label) => data?.[label] || 0)

  return (
    <div className="chart-card">
      <h3>{title}</h3>
      <div className="chart-body">
        <Doughnut
          data={{
            labels: SENTIMENT_LABELS,
            datasets: [
              {
                data: values,
                backgroundColor: SENTIMENT_COLORS,
                borderWidth: 0,
              },
            ],
          }}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { labels: { color: '#7c8db5' } },
              tooltip: { backgroundColor: '#0f1629', borderColor: '#1f2e4d', borderWidth: 1 },
            },
          }}
        />
      </div>
    </div>
  )
}

export default SentimentChart
