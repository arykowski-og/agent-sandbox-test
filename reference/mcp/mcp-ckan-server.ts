import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from 'zod';
import * as fs from 'fs'; // Import fs for file logging
import * as util from 'util'; // Import util for formatting
// Removed problematic import for @modelcontextprotocol/sdk/types
// Will use 'any' or infer types where ResponseMessage was intended for now.

// --- File Logging Setup ---
const logFile = fs.createWriteStream('mcp-server-debug.log', { flags: 'a' });
const logStdout = process.stdout;

console.log = function(...args: any[]) {
  logFile.write(util.format.apply(null, args as any) + '\n');
  logStdout.write(util.format.apply(null, args as any) + '\n');
};
console.error = function(...args: any[]) {
  logFile.write(util.format.apply(null, args as any) + '\n');
  logStdout.write(util.format.apply(null, args as any) + '\n'); // also log errors to stdout for visibility if possible
};
// --- End File Logging Setup ---

const DEFAULT_CKAN_BASE_URL = process.env.CKAN_BASE_URL || 'https://ckantesting.ogopendata.com';

// --- Tool Execution Logic (remains the same) ---
interface SearchDatasetsParams {
  query: string;
  baseUrl?: string;
  rows?: number;
  start?: number;
}

interface GetDatasetDetailsParams {
  id: string;
  baseUrl?: string;
}

async function executeSearchDatasets({ query, baseUrl, rows = 5, start = 0 }: SearchDatasetsParams) {
  const effectiveBaseUrl = baseUrl || DEFAULT_CKAN_BASE_URL;
  const url = `${effectiveBaseUrl}/api/3/action/package_search?q=${encodeURIComponent(query)}&rows=${rows}&start=${start}`;
  console.log(`[MCP Server - executeSearchDatasets] Requesting CKAN URL: ${url}`);

  const response = await fetch(url);
  const responseText = await response.text();

  if (!response.ok) {
    console.error('[MCP Server - executeSearchDatasets] CKAN API Error Response Text:', responseText);
    console.error('[MCP Server - searchDatasets] CKAN API Error Details:', { status: response.status, statusText: response.statusText });
    throw new Error(`CKAN package_search failed: ${response.status} ${response.statusText} - ${responseText}`);
  }

  let data;
  try {
    data = JSON.parse(responseText);
  } catch (e: any) {
    console.error('[MCP Server - executeSearchDatasets] Failed to parse CKAN JSON response:', responseText);
    throw new Error(`Failed to parse CKAN API response: ${e.message}`);
  }
  
  console.log('[MCP Server - executeSearchDatasets] Raw CKAN API Response Data:', JSON.stringify(data, null, 2));

  if (data.success && data.result) {
    const conciseResults = data.result.results.map((dataset: any) => ({
      id: dataset.id,
      title: dataset.title,
      notes: dataset.notes ? dataset.notes.substring(0, 150) + (dataset.notes.length > 150 ? '...' : '') : 'No description available.',
      organization_title: dataset.organization?.title,
    }));
    return {
      count: data.result.count,
      results: conciseResults,
    };
  }
  return { count: 0, results: [] };
}

async function executeGetDatasetDetails({ id, baseUrl }: GetDatasetDetailsParams) {
  const resolvedBaseUrl = baseUrl || DEFAULT_CKAN_BASE_URL;
  // console.log(`[MCP Server - getDatasetDetails] Requesting URL: ${url}`);
  const url = `${resolvedBaseUrl}/api/3/action/package_show?id=${encodeURIComponent(id)}`;
  const response = await fetch(url);
  if (!response.ok) {
    const errorText = await response.text();
    console.error(`[MCP Server - getDatasetDetails] CKAN API error: ${response.status} ${response.statusText}`, errorText);
    throw new Error(`CKAN API request for dataset details failed: ${response.status} ${response.statusText}`);
  }
  const fullApiResponse = await response.json();
  if (!fullApiResponse.success || !fullApiResponse.result) {
    console.error('[MCP Server - getDatasetDetails] CKAN API call did not return a successful result or result is missing.', fullApiResponse);
    throw new Error('Failed to retrieve successful dataset details from CKAN API.');
  }
  const data = fullApiResponse.result;
  const essentialData = {
    id: data.id,
    title: data.title,
    name: data.name,
    notes: data.notes ? (data.notes.length > 500 ? data.notes.substring(0, 497) + '...' : data.notes) : 'No description provided.',
    organization_title: data.organization?.title,
    num_resources: data.num_resources,
    num_tags: data.num_tags,
    tags: data.tags?.map((tag: { display_name?: string; name?: string }) => tag.display_name || tag.name).slice(0, 5),
    resources_summary: data.resources?.slice(0, 3).map((r: { name?: string; format?: string; url?: string }) => ({
      name: r.name,
      format: r.format,
      url: r.url,
    })),
    license_title: data.license_title,
    metadata_created: data.metadata_created,
    metadata_modified: data.metadata_modified,
    url: `${resolvedBaseUrl}/dataset/${data.name}`,
  };
  return essentialData;
  // Removed manual error object construction; throwing errors directly is preferred for low-level server.
}
// --- End of Tool Execution Logic ---

const server = new McpServer({
  name: "ckan-mcp-server",
  version: "1.0.0",
});

// Schemas for tool parameters (raw shapes for server.tool, ZodObjects for inference)
const searchCKANDatasetsParamsShape = {
  query: z.string().describe('Search keywords or query string for datasets'),
  baseUrl: z.string().url().optional().describe('CKAN instance base URL'),
  rows: z.number().int().min(1).max(100).optional().default(5),
  start: z.number().int().min(0).optional().default(0),
};
const SearchCKANDatasetsParamsSchema = z.object(searchCKANDatasetsParamsShape);

const getCKANDatasetDetailsParamsShape = {
  id: z.string().describe('Dataset name or id'),
  baseUrl: z.string().url().optional().describe('CKAN instance base URL'),
};
const GetCKANDatasetDetailsParamsSchema = z.object(getCKANDatasetDetailsParamsShape);

// Register tools using server.tool()
server.tool(
  "searchCKANDatasets",
  searchCKANDatasetsParamsShape, // Use the raw shape
  async (params: z.infer<typeof SearchCKANDatasetsParamsSchema>) => {
    console.log(`[MCP Server] Handling tool call: searchCKANDatasets`);
    try {
      const result = await executeSearchDatasets(params);
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    } catch (error: any) {
      console.error(`[MCP Server Tool Error - searchCKANDatasets]: ${error.message}`);
      // McpServer will handle formatting this error into an MCP error response
      throw error;
    }
  }
);

server.tool(
  "getCKANDatasetDetails",
  getCKANDatasetDetailsParamsShape, // Use the raw shape
  async (params: z.infer<typeof GetCKANDatasetDetailsParamsSchema>) => {
    console.log(`[MCP Server] Handling tool call: getCKANDatasetDetails`);
    try {
      const result = await executeGetDatasetDetails(params);
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    } catch (error: any) {
      console.error(`[MCP Server Tool Error - getCKANDatasetDetails]: ${error.message}`);
      // McpServer will handle formatting this error into an MCP error response
      throw error;
    }
  }
);

async function main() {
  console.log("<<<<< RUNNING MCP SERVER WITH McpServer CLASS - v2 >>>>>"); // Unique marker
  console.log("Starting MCP server with StdioTransport using McpServer class...");
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log("MCP Server (McpServer class) connected via Stdio.");
  console.log("Server is ready to handle tool calls (searchCKANDatasets, getCKANDatasetDetails).");
}

main().catch(error => {
  console.error("Failed to start MCP server:", error);
  process.exit(1); // Exit if server fails to start
});

// To run this server:
// 1. Compile: pnpm tsc (ensure tsconfig.json has outDir set, e.g., "dist")
// 2. Run: node dist/lib/ai/mcp/mcp-ckan-server.js
// Ensure CKAN_BASE_URL is in your .env or environment if not using the default. 