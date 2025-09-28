import { createAPIClient } from '@/lib/api';
import { listFlowsApiV1FlowsGet } from '@yeetflow/api-client';
import FlowsWithUI from './with-ui';
import { startFlowFormAction } from './actions';

export default async function FlowsPage() {
  const client = createAPIClient();
  const response = await listFlowsApiV1FlowsGet({ client, throwOnError: true });
  const flows = response.data.flows;

  return <FlowsWithUI flows={flows} startFlow={startFlowFormAction} />;
}
