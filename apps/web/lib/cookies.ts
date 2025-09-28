import { NextResponse } from 'next/server';

type CookieStore = ReturnType<typeof NextResponse.json>['cookies'];
type CookieOptions = Parameters<CookieStore['set']>[2];

type ParsedCookie = {
  name: string;
  value: string;
  options: Partial<CookieOptions>;
};

export function parseSetCookieHeader(
  cookieHeader: string,
  isSecureRequest: boolean,
): ParsedCookie | null {
  const segments: string[] = [];
  let buffer = '';
  let inQuotes = false;

  for (let i = 0; i < cookieHeader.length; i += 1) {
    const char = cookieHeader[i];
    if (char === '"' && cookieHeader[i - 1] !== '\\') {
      inQuotes = !inQuotes;
    }

    if (char === ';' && !inQuotes) {
      segments.push(buffer.trim());
      buffer = '';
      continue;
    }

    buffer += char;
  }

  if (buffer) {
    segments.push(buffer.trim());
  }

  const [nameValue, ...attributePairs] = segments.filter(Boolean);

  if (!nameValue || !nameValue.includes('=')) return null;

  const [rawName, ...rawValueParts] = nameValue.split('=');
  const name = rawName ?? '';
  const value = rawValueParts.join('=');

  const options: Partial<CookieOptions> = {};
  let requestedSameSite: 'lax' | 'strict' | 'none' | undefined;

  attributePairs.forEach((attribute) => {
    const [attrNameRaw, ...attrValueParts] = attribute.split('=');
    const attrName = attrNameRaw?.toLowerCase();
    const attrValue = attrValueParts.join('=');

    switch (attrName) {
      case 'path':
        options.path = attrValue || undefined;
        break;
      case 'domain':
        options.domain = attrValue || undefined;
        break;
      case 'samesite':
        if (attrValue) {
          const sameSite = attrValue.toLowerCase();
          if (
            sameSite === 'lax' ||
            sameSite === 'strict' ||
            sameSite === 'none'
          ) {
            requestedSameSite = sameSite;
          }
        }
        break;
      case 'max-age':
        if (attrValue) {
          const maxAge = Number(attrValue);
          if (!Number.isNaN(maxAge)) {
            options.maxAge = maxAge;
          }
        }
        break;
      case 'expires':
        if (attrValue) {
          const timestamp = Date.parse(attrValue);
          if (!Number.isNaN(timestamp)) {
            options.expires = new Date(timestamp);
          }
        }
        break;
      case 'priority':
        if (attrValue) {
          const priority = attrValue.toLowerCase();
          if (
            priority === 'low' ||
            priority === 'medium' ||
            priority === 'high'
          ) {
            options.priority = priority;
          }
        }
        break;
      case 'partitioned':
        options.partitioned = true;
        break;
      case 'httponly':
        options.httpOnly = true;
        break;
      case 'secure':
        options.secure = true;
        break;
      default:
        break;
    }
  });

  if (requestedSameSite) {
    options.sameSite = requestedSameSite;
  }

  if (!isSecureRequest) {
    delete options.secure;
    if (options.sameSite === 'none') {
      options.sameSite = 'lax';
    }
    // CHIPS: Partitioned requires Secure + SameSite=None; remove in dev/insecure.
    if (options.partitioned) {
      delete options.partitioned;
    }
  }

  // Always strip upstream Domain when proxying to the web origin
  delete options.domain;

  return { name, value, options };
}
