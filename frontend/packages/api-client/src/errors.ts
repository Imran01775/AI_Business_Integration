import { parseApiError } from "@sales-agent/shared";

export { ApiError, parseApiError } from "@sales-agent/shared";

export async function throwIfNotOk(response: Response): Promise<void> {
  if (response.ok) {
    return;
  }
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  throw parseApiError(response.status, body);
}
