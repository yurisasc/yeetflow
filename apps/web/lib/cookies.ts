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
  const [nameValue, ...attributePairs] = cookieHeader
    .split(';')
    .map((part) => part.trim())
    .filter(Boolean);

  if (!nameValue) return null;

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
          if (sameSite === 'lax' || sameSite === 'strict' || sameSite === 'none') {
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
          const expires = new Date(attrValue);
          if (!Number.isNaN(expires.valueOf())) {
            options.expires = expires;
          }
        }
        break;
      case 'priority':
        if (attrValue) {
          const priority = attrValue.toLowerCase();
          if (priority === 'low' || priority === 'medium' || priority === 'high') {
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
  }

  return { name, value, options };
}
