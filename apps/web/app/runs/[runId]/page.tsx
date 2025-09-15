import { notFound } from 'next/navigation'

interface RunPageProps {
  params: Promise<{ runId: string }>
}

export default async function RunPage({ params }: RunPageProps) {
  const { runId } = await params

  // TODO: Fetch run status from worker API
  // For now, show a placeholder
  const run = {
    id: runId,
    status: 'running',
    sessionUrl: 'https://example.com/session',
  }

  if (!run) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Run {runId}</h1>
      <div className="mb-4">
        <span className="font-semibold">Status:</span> {run.status}
      </div>
      <div className="border rounded-lg p-4">
        <h2 className="text-xl font-semibold mb-2">Browser Session</h2>
        {/* TODO: Embed session URL in iframe */}
        <div className="w-full h-96 bg-gray-200 rounded flex items-center justify-center">
          <p className="text-gray-500">Session iframe will be embedded here</p>
        </div>
      </div>
    </div>
  )
}
