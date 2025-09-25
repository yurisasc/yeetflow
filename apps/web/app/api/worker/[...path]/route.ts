import { NextRequest, NextResponse } from 'next/server';

const WORKER_BASE_URL = process.env.WORKER_BASE_URL || 'http://localhost:8000';
const WORKER_API_TOKEN = process.env.WORKER_API_TOKEN;

type RouteContext = { params: Promise<{ path: string[] }> };

async function resolvePath(context: RouteContext): Promise<string[]> {
  const { path } = await context.params;
  return path;
}

export async function GET(request: NextRequest, context: RouteContext) {
  const path = await resolvePath(context);
  return proxyRequest(request, path);
}

export async function POST(request: NextRequest, context: RouteContext) {
  const path = await resolvePath(context);
  return proxyRequest(request, path);
}

export async function PUT(request: NextRequest, context: RouteContext) {
  const path = await resolvePath(context);
  return proxyRequest(request, path);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  const path = await resolvePath(context);
  return proxyRequest(request, path);
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  const path = await resolvePath(context);
  return proxyRequest(request, path);
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
): Promise<NextResponse> {
  try {
    // Build the target URL
    const path = pathSegments.join('/');
    const targetUrl = `${WORKER_BASE_URL}/${path}`;

    // Get the original URL and remove the /api/worker prefix
    const url = new URL(request.url);
    const searchParams = url.searchParams.toString();
    const fullTargetUrl = searchParams
      ? `${targetUrl}?${searchParams}`
      : targetUrl;

    // Prepare headers
    const headers = new Headers();
    for (const [key, value] of request.headers.entries()) {
      // Skip host header as it will be set by fetch
      if (key.toLowerCase() !== 'host') {
        headers.set(key, value);
      }
    }

    // Add API token only if no user Authorization header (T016)
    const existingAuth = request.headers.get('authorization');
    if (!existingAuth && WORKER_API_TOKEN) {
      headers.set('Authorization', `Bearer ${WORKER_API_TOKEN}`);
    }

    // Make the request to the worker
    const response = await fetch(fullTargetUrl, {
      method: request.method,
      headers,
      body:
        request.method !== 'GET' && request.method !== 'HEAD'
          ? await request.text()
          : undefined,
    });

    // Create response with the worker's response
    const responseHeaders = new Headers();
    for (const [key, value] of response.headers.entries()) {
      responseHeaders.set(key, value);
    }

    const responseBody = await response.text();

    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to proxy request to worker' },
      { status: 500 },
    );
  }
}
