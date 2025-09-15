import Link from 'next/link'

// TODO: Load flows from local config
const flows = [
  { id: '1', name: 'Sample Flow 1', description: 'A sample automation flow' },
  { id: '2', name: 'Sample Flow 2', description: 'Another sample automation flow' },
]

export default function FlowsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Available Flows</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {flows.map((flow) => (
          <div key={flow.id} className="border rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-2">{flow.name}</h2>
            <p className="text-gray-600 mb-4">{flow.description}</p>
            <Link
              href={`/runs/${flow.id}`}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Start Flow
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}
