import { CkanAgentState } from './state';
import { type UIMessage, type TextPart } from 'ai';
// Assuming myProvider and selectedChatModel are accessible or passed appropriately
// This might require refactoring how providers/models are accessed within graph nodes
// For now, let's assume we can import them or they are part of a broader context/config
import { myProvider } from '@/lib/ai/providers'; // Adjust path if needed
import { ChatOpenAI } from '@langchain/openai'; // Or your specific LLM class
import { 
    HumanMessage, 
    SystemMessage, 
    AIMessage, 
    BaseMessage 
} from "@langchain/core/messages";
import { type BaseChatModel } from "@langchain/core/language_models/chat_models"; // For typing the LLM
import { generateUUID } from '@/lib/utils'; // For generating message IDs
import { summarizeSearchDatasets, summarizeDatasetDetails, type DatasetDetails } from '@/lib/ai/tools/summarize-tool-results';
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { z } from 'zod';

// --- MCP Client Setup ---
// This client should ideally be a singleton or managed instance, not recreated on every node call.
// For this example, we'll initialize it. Consider where to best manage its lifecycle.
let mcpClient: Client | null = null;
let mcpClientPromise: Promise<Client> | null = null;

async function getMcpClient(): Promise<Client> {
  if (mcpClient) {
    return mcpClient;
  }
  if (mcpClientPromise) {
    return mcpClientPromise;
  }

  mcpClientPromise = (async () => {
    const client = new Client({
      name: "langgraph-ckan-agent-client",
      version: "1.0.0",
    });

    // Path to the compiled MCP server script, now in lib/ai/mcp/
    // Assuming compilation places it in dist/lib/ai/mcp/mcp-ckan-server.js
    const transport = new StdioClientTransport({
      command: "node",
      args: ["dist/lib/ai/mcp/mcp-ckan-server.js"]
    });

    try {
      console.log("[CKAN Agent Node] Connecting to MCP server via StdioClientTransport...");
      await client.connect(transport);
      console.log("[CKAN Agent Node] Successfully connected to MCP server.");
      mcpClient = client;
      return client;
    } catch (error) {
      console.error("[CKAN Agent Node] Failed to connect to MCP server:", error);
      mcpClientPromise = null;
      throw error;
    }
  })();
  return mcpClientPromise;
}
// --- End MCP Client Setup ---

// --- MCP Request Schemas (mirrored from mcp-ckan-server.ts) ---
const SearchCKANDatasetsParamsSchema = z.object({
    query: z.string().describe('Search keywords or query string for datasets'),
    baseUrl: z.string().url().optional().describe('CKAN instance base URL'),
    rows: z.number().int().min(1).max(100).optional().default(5),
    start: z.number().int().min(0).optional().default(0),
  });
  
const SearchCKANDatasetsRequestSchema = z.object({
    method: z.literal("searchCKANDatasets"),
    params: SearchCKANDatasetsParamsSchema,
});
  
const GetCKANDatasetDetailsParamsSchema = z.object({
    id: z.string().describe('Dataset name or id'),
    baseUrl: z.string().url().optional().describe('CKAN instance base URL'),
});
  
const GetCKANDatasetDetailsRequestSchema = z.object({
    method: z.literal("getCKANDatasetDetails"),
    params: GetCKANDatasetDetailsParamsSchema,
});
// --- End MCP Request Schemas ---

// Placeholder for node functions. Each will take state and return partial state.

export async function llmIntentNode(state: CkanAgentState): Promise<Partial<CkanAgentState>> {
  console.log('[CKAN Agent Node] Executing llmIntentNode');
  const { messages, selectedChatModel } = state;

  if (!selectedChatModel) {
    return { error: 'Chat model not selected.', nextAction: 'END' };
  }

  let llm: BaseChatModel;

  if (selectedChatModel === 'chat-model') {
    llm = new ChatOpenAI({
      modelName: "gpt-4o",
      temperature: 0.2, // Lower temperature for more deterministic JSON output
      // apiKey: process.env.OPENAI_API_KEY, 
    });
  } else {
    console.error(`[CKAN Agent Node] llmIntentNode: Model "${selectedChatModel}" is not configured for direct LangChain LLM instantiation in this node. OPENAI_API_KEY must be set for gpt-4o.`);
    return { error: `Model ${selectedChatModel} not supported for LangChain operations in intent node.`, nextAction: 'END' };
  }

  const userMessage = messages.findLast(msg => msg.role === 'user');

  if (!userMessage?.content) {
    return { error: 'No user message content found to determine intent.', nextAction: 'END' };
  }
  const currentInput = Array.isArray(userMessage.content) ? userMessage.content.map(p => p.type === 'text' ? p.text : '').join('') : userMessage.content;

  const ckanToolDescriptions = `
You can interact with open data using CKAN tools. Based on the user's message, determine the most appropriate action and any necessary parameters.
Available actions:
- "searchDatasets": To find datasets by keywords.
  - Parameters: "keywords" (string, required)
- "getDatasetDetails": To get detailed information about a specific dataset.
  - Parameters: "datasetId" (string, required)
- "listOrganizations": To list available organizations/publishers of data.
  - Parameters: None directly, but you can use "keywords" (string, optional) to filter or search if the user implies a specific type of organization.
- "getOrganizationDetails": To get details about a specific organization.
  - Parameters: "organizationId" (string, required)
- "listTags": To discover tags or find specific tags by a query.
  - Parameters: "keywords" (string, optional, to search for specific tags)
- "searchDatasetsByTag": To find datasets associated with a specific tag.
  - Parameters: "tagToSearchBy" (string, required)
- "END": If no specific CKAN action is implied or if the query is general conversation.

Special instructions for "searchDatasets":
- The tool returns a \`count\` of total datasets found and a \`results\` array of the datasets for the current page.
- If \`count\` is greater than the number of items in the listed \`results\`, briefly mention that more datasets are available (e.g., 'I found X total datasets. Here are the first Y: ...').
- If \`count\` is exactly 1, you should then automatically suggest or imply "getDatasetDetails" for that single dataset (using its \`id\` from the search result) as the next logical step or directly ask the user if they want details for it.

Based on the user's message: "${currentInput}"

Respond with a JSON object with the following structure:
{
  "action": "searchDatasets" | "getDatasetDetails" | "listOrganizations" | "getOrganizationDetails" | "listTags" | "searchDatasetsByTag" | "END",
  "keywords": "string" | null,      // For "searchDatasets", "listOrganizations" (optional), "listTags" (optional)
  "datasetId": "string" | null,    // For "getDatasetDetails"
  "organizationId": "string" | null, // For "getOrganizationDetails"
  "tagToSearchBy": "string" | null   // For "searchDatasetsByTag"
}

- Set "keywords", "datasetId", "organizationId", "tagToSearchBy" to null if not applicable to the chosen action or if the information isn't provided/derivable.
- If the user's query is ambiguous for an ID required by an action (e.g., "getDatasetDetails", "getOrganizationDetails"), lean towards "searchDatasets" if keywords are present, "listOrganizations" or "listTags" if relevant, or "END".
`;
  
  const promptMessagesForLLM: BaseMessage[] = [
    new SystemMessage(ckanToolDescriptions),
    new HumanMessage(currentInput) 
  ];

  try {
    console.log(`[CKAN Agent Node] Invoking LLM for intent with model: ${selectedChatModel}`);
    const response: BaseMessage = await llm.invoke(promptMessagesForLLM);
    
    let llmResponseContent = '';
    if (typeof response.content === 'string') {
        llmResponseContent = response.content.trim();
    } else if (Array.isArray(response.content)) {
        llmResponseContent = response.content
            .filter((part: any) => part.type === 'text')
            .map((part: any) => part.text)
            .join('')
            .trim();
    } else {
        console.error('[CKAN Agent Node] LLM response content is not a string or expected array structure:', response.content);
        return { error: 'LLM response format error for intent.', nextAction: 'END' };
    }

    console.log(`[CKAN Agent Node] LLM raw response for intent: "${llmResponseContent}"`);

    let parsedIntent: { 
        action: string; 
        keywords?: string | null; 
        datasetId?: string | null;
        organizationId?: string | null;
        tagToSearchBy?: string | null;
    };
    let jsonStringToParse = llmResponseContent.trim(); 

    try {
      const markdownMatch = llmResponseContent.match(/```(?:json)?\s*\n?(\{[\s\S]*?\})\s*\n?```/s);
      if (markdownMatch && markdownMatch[1]) {
        jsonStringToParse = markdownMatch[1].trim(); 
      }
      
      parsedIntent = JSON.parse(jsonStringToParse);
      console.log('[CKAN Agent Node] Parsed LLM intent:', parsedIntent);
    } catch (e) {
      console.error('[CKAN Agent Node] Failed to parse LLM intent JSON:', e, `Attempted to parse: "${jsonStringToParse}"`, `Original LLM content: "${llmResponseContent}"`);
      return { error: 'Failed to parse LLM intent from response.', nextAction: 'END' };
    }
    
    const validActions = ['searchDatasets', 'getDatasetDetails', 'listOrganizations', 'getOrganizationDetails', 'listTags', 'searchDatasetsByTag', 'END'];
    const nextActionVal = validActions.includes(parsedIntent.action) ? parsedIntent.action : 'END';
    
    let intentSummaryText = `Understood. Planning to perform action: ${nextActionVal}.`;
    if (nextActionVal === 'searchDatasets' && parsedIntent.keywords) {
        intentSummaryText = `Okay, I'll search for datasets related to "${parsedIntent.keywords}".`;
    } else if (nextActionVal === 'getDatasetDetails' && parsedIntent.datasetId) {
        intentSummaryText = `Okay, I'll get details for dataset ID "${parsedIntent.datasetId}".`;
    } else if (nextActionVal === 'listOrganizations') {
        intentSummaryText = parsedIntent.keywords 
            ? `Okay, I'll list organizations related to "${parsedIntent.keywords}".` 
            : "Okay, I'll list available organizations.";
    } else if (nextActionVal === 'getOrganizationDetails' && parsedIntent.organizationId) {
        intentSummaryText = `Okay, I'll get details for organization ID "${parsedIntent.organizationId}".`;
    } else if (nextActionVal === 'listTags') {
        intentSummaryText = parsedIntent.keywords
            ? `Okay, I'll search for tags related to "${parsedIntent.keywords}".`
            : "Okay, I'll list available tags.";
    } else if (nextActionVal === 'searchDatasetsByTag' && parsedIntent.tagToSearchBy) {
        intentSummaryText = `Okay, I'll search for datasets with the tag "${parsedIntent.tagToSearchBy}".`;
    } else if (nextActionVal === 'END') {
        intentSummaryText = "How can I help you further with open data today?";
    }
    
    const textPart: TextPart = { type: 'text', text: intentSummaryText };
    const assistantUIMessage: UIMessage = {
        id: generateUUID(),
        role: 'assistant',
        content: intentSummaryText, 
        parts: [textPart],
        displayType: 'thinking', 
    } as any;

    console.log(`[CKAN Agent Node] Intent determined by LLM: ${nextActionVal}, Keywords: ${parsedIntent.keywords}, DatasetID: ${parsedIntent.datasetId}, OrganizationID: ${parsedIntent.organizationId}, TagToSearchBy: ${parsedIntent.tagToSearchBy}`);
    return { 
        nextAction: nextActionVal, 
        searchKeywords: parsedIntent.keywords || undefined,
        identifiedDatasetId: parsedIntent.datasetId || undefined,
        identifiedOrganizationId: parsedIntent.organizationId || undefined,
        tagToSearchBy: parsedIntent.tagToSearchBy || undefined,
        messages: [...messages, assistantUIMessage] 
    };

  } catch (e: any) {
    console.error('[CKAN Agent Node] Error invoking LLM for intent:', e);
    return { error: `LLM invocation failed: ${e.message}`, nextAction: 'END' };
  }
}

export async function searchDatasetsNode(state: CkanAgentState): Promise<Partial<CkanAgentState>> {
  console.log('[CKAN Agent Node] Executing searchDatasetsNode');
  const { messages, userInput, searchKeywords } = state; 
  console.log(`[CKAN Agent Node - searchDatasetsNode] Received state - userInput: "${userInput}", searchKeywords: "${searchKeywords}"`); // Log received state
  
  let query: string | undefined = searchKeywords; 

  if (!query) { 
    query = userInput;
    if (!query) {
      const lastUserMessage = messages.findLast(msg => msg.role === 'user');
      if (lastUserMessage?.content) {
        query = Array.isArray(lastUserMessage.content) 
                ? lastUserMessage.content.map(p => p.type === 'text' ? p.text : '').join('') 
                : lastUserMessage.content;
      }
    }
  }
  
  if (!query) {
    const errorMsg = 'Search query missing for searchDatasetsNode';
    return { 
        error: errorMsg, 
        messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorMsg, parts: [{type: 'text', text: errorMsg}]}] 
    };
  }

  try {
    const client = await getMcpClient();
    console.log(`[CKAN Agent Node] Calling MCP tool "searchCKANDatasets" with query: "${query}"`);
    
    const toolArgs = { query: query as string, rows: 5, start: 0 }; // These are the 'params' for the server

    const toolResult: any = await client.callTool({
        name: "searchCKANDatasets", 
        arguments: toolArgs
    });
    console.log("[CKAN Agent Node - searchDatasetsNode] Raw toolResult from client.callTool:", JSON.stringify(toolResult, null, 2));

    let searchResultsDataString: string;
    if (toolResult && Array.isArray(toolResult.content) && toolResult.content.length > 0 && toolResult.content[0] && typeof toolResult.content[0].text === 'string') {
        searchResultsDataString = toolResult.content[0].text;
    } else if (typeof toolResult === 'string') { // Fallback if the result is already a direct string
        searchResultsDataString = toolResult;
    } else {
        console.error("[CKAN Agent Node] MCP tool result is not in the expected string format:", JSON.stringify(toolResult, null, 2));
        const errorMsg = "Unexpected data format from search service.";
        return { 
            error: errorMsg, 
            messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorMsg, parts: [{type: 'text', text: errorMsg}]}] 
        };
    }

    let parsedResult;
    try {
      parsedResult = JSON.parse(searchResultsDataString);
    } catch (e: any) {
      console.error("[CKAN Agent Node] Failed to parse MCP tool result JSON:", searchResultsDataString, e);
      const errorMsg = "Error processing data from search service.";
      return { 
          error: errorMsg, 
          messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorMsg, parts: [{type: 'text', text: errorMsg}]}] 
      };
    }

    // Now parsedResult should be: { count: number, results: Array<{id: string, title: string, ...}> }
    const summary = summarizeSearchDatasets(parsedResult); 
    
    const textPart: TextPart = { type: 'text', text: summary };
    const assistantMessage: UIMessage = { 
        id: generateUUID(), 
        role: 'assistant', 
        content: summary, 
        parts: [textPart] 
    };
    console.log(`[CKAN Agent Node] searchDatasetsNode MCP result: ${summary}`);
    return { 
        searchResults: parsedResult.results, 
        lastSummary: summary, 
        messages: [...messages, assistantMessage],
        nextAction: 'END' 
    };
  } catch (e: any) {
    console.error('[CKAN Agent Node] Error in searchDatasetsNode (MCP call):', e);
    const errorSummary = `Error searching datasets via MCP: ${e.message}`;
    const errorTextPart: TextPart = { type: 'text', text: errorSummary };
    return { 
        error: errorSummary, 
        messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorSummary, parts: [errorTextPart]}] 
    };
  }
}

export async function getDatasetDetailsNode(state: CkanAgentState): Promise<Partial<CkanAgentState>> {
  console.log('[CKAN Agent Node] Executing getDatasetDetailsNode');
  const { messages, userInput, searchResults, nextAction, identifiedDatasetId } = state; // Added identifiedDatasetId

  let datasetId: string | undefined = identifiedDatasetId; // Prioritize identifiedDatasetId

  if (!datasetId) { // Fallback logic
    if (nextAction === 'getDatasetDetails' && userInput) {
      // Attempt to extract ID from user input if llmIntentNode didn't provide one,
      // but llmIntentNode is now primarily responsible for this.
      // This could be simplified or removed if llmIntentNode is reliable.
      datasetId = userInput; 
      console.log(`[CKAN Agent Node] Using userInput as datasetId: "${datasetId}" because identifiedDatasetId was null and nextAction was getDatasetDetails.`);
    } else if (searchResults && searchResults.length > 0) {
      // If no specific ID, and previous search results exist, pick the first one.
      // This behavior might need to be refined (e.g., only if count was 1).
      // The LLM in llmIntentNode should ideally handle the "count is 1, so get details" logic.
      datasetId = searchResults[0].id;
      console.log(`[CKAN Agent Node] Using first searchResult ID as datasetId: "${datasetId}" because identifiedDatasetId and userInput for ID were null.`);
    }
  }

  if (!datasetId) {
    const errorMsg = 'Dataset ID missing for getDatasetDetailsNode';
    console.warn('[CKAN Agent Node] No datasetId found. Current state:', { searchResults, userInput, nextAction });
    const errorTextPart: TextPart = { type: 'text', text: errorMsg };
    return { 
        error: errorMsg, 
        messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorMsg, parts: [errorTextPart]}] 
    };
  }

  try {
    const client = await getMcpClient();
    console.log(`[CKAN Agent Node] Calling MCP tool "getCKANDatasetDetails" with ID: "${datasetId}"`);

    const toolArgs = { id: datasetId as string }; // These are the 'params' for the server
    
    const toolResult: any = await client.callTool({
        name: "getCKANDatasetDetails", // Matches method literal in server's request schema
        arguments: toolArgs
    });
    // Add a log to see the raw result for this node too, if needed for future debugging
    console.log("[CKAN Agent Node - getDatasetDetailsNode] Raw toolResult from client.callTool:", JSON.stringify(toolResult, null, 2)); 

    let detailsDataString: string;
    if (toolResult && Array.isArray(toolResult.content) && toolResult.content.length > 0 && toolResult.content[0] && typeof toolResult.content[0].text === 'string') {
        detailsDataString = toolResult.content[0].text;
    } else if (typeof toolResult === 'string') { // Fallback if the result is already a direct string
        detailsDataString = toolResult;
    } else {
        console.error("[CKAN Agent Node] MCP tool result for getDatasetDetails is not in the expected string format:", JSON.stringify(toolResult, null, 2));
        const errorMsg = "Unexpected data format from dataset details service.";
        return { 
            error: errorMsg, 
            messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorMsg, parts: [{type: 'text', text: errorMsg}]}] 
        };
    }

    let detailsData;
    try {
      detailsData = JSON.parse(detailsDataString);
    } catch (e: any) {
      console.error("[CKAN Agent Node] Failed to parse MCP tool result JSON for getDatasetDetails:", detailsDataString, e);
      const errorMsg = "Error processing data from dataset details service.";
      return { 
          error: errorMsg, 
          messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorMsg, parts: [{type: 'text', text: errorMsg}]}] 
      };
    }

    // Assuming detailsData is now correctly typed based on the server's actual return for this method.
    const summary = summarizeDatasetDetails(detailsData as DatasetDetails);
    
    const textPart: TextPart = { type: 'text', text: summary };
    const assistantMessage: UIMessage = { 
        id: generateUUID(), 
        role: 'assistant', 
        content: summary, 
        parts: [textPart] 
    };
    console.log(`[CKAN Agent Node] getDatasetDetailsNode MCP result: ${summary}`);
    return { 
        datasetDetails: detailsData as DatasetDetails, 
        lastSummary: summary, 
        messages: [...messages, assistantMessage] 
    };
  } catch (e: any) {
    console.error('[CKAN Agent Node] Exception in getDatasetDetailsNode (MCP call):', e);
    const errorSummary = `Error getting dataset details via MCP: ${e.message}`;
    const errorTextPart: TextPart = { type: 'text', text: errorSummary };
    return { 
        error: errorSummary, 
        messages: [...messages, {id: generateUUID(), role: 'assistant', content: errorSummary, parts: [errorTextPart]}] 
    };
  }
}

// Add other nodes as per langgraph-refactor-plan.md
// e.g., conditionalBranchNode, summarizeDatasetNode, downloadAndPreviewCsvNode, humanInTheLoopNode 