import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  // TODO: remove this when we have a proper API
  // Will need to have the dev server running to generate the API client
  input: "http://localhost:8000/openapi.json",
  output: "src/generated",
  plugins: [
    {
      name: "@hey-api/client-next",
      runtimeConfigPath: "../config",
    },
  ],
});
