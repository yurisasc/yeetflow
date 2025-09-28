import {
  getRunApiV1RunsRunIdGet,
  getRunSessionsApiV1RunsRunIdSessionsGet,
  getFlowApiV1FlowsFlowIdGet,
  type RunRead,
  type FlowRead,
} from '@yeetflow/api-client';
import { createAPIClient } from '@/lib/api';
import RunPageWithUI from './with-ui';

type PageProps = { params: Promise<{ id: string }> };

export default async function RunPage(props: PageProps) {
  const { id } = await props.params;

  const client = createAPIClient();

  let run: RunRead | null = null;
  let flow: FlowRead | null = null;
  let sessionUrl: string | null = null;
  let errorMessage: string | null = null;

  try {
    const runRes = await getRunApiV1RunsRunIdGet({
      client,
      path: { run_id: id },
      throwOnError: true,
    });
    run = runRes.data;

    // Flow details for display
    if (run?.flow_id) {
      const flowRes = await getFlowApiV1FlowsFlowIdGet({
        client,
        path: { flow_id: run.flow_id },
        throwOnError: false,
      });
      flow = flowRes.data ?? null;
    }

    // Sessions to extract session_url
    const sessionsRes = await getRunSessionsApiV1RunsRunIdSessionsGet({
      client,
      path: { run_id: id },
      throwOnError: false,
    });
    const sessions = (sessionsRes.data as any[]) || [];
    sessionUrl =
      sessions.find((s) => s?.session_url)?.session_url ?? null;
  } catch (err: any) {
    const status = err?.response?.status;
    if (status === 404) errorMessage = 'Run not found. The ID may be invalid.';
    else if (status === 403)
      errorMessage = 'Permission denied. You do not have access to this run.';
    else errorMessage = 'Failed to load run details. Please try again later.';
  }

  return (
    <RunPageWithUI
      run={run}
      flow={flow}
      sessionUrl={sessionUrl}
      errorMessage={errorMessage}
    />
  );
}
