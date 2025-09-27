import type { CreateClientConfig } from "./generated/client";

export const createClientConfig: CreateClientConfig = (override) => ({
  ...(override ?? {}),
  credentials: "include",
});
