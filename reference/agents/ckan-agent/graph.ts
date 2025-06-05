import { StateGraph, END } from '@langchain/langgraph';
import { type CkanAgentState } from './state';
import { llmIntentNode, searchDatasetsNode, getDatasetDetailsNode } from './nodes';
import { UIMessage } from 'ai'; // Keep UIMessage for channel definition

// Define the state graph
const workflow = new StateGraph<CkanAgentState>({
  channels: {
    messages: {
      value: (x: UIMessage[], y: UIMessage[]) => x.concat(y),
      default: () => [],
    },
    userInput: null, 
    searchResults: null,
    datasetDetails: null,
    lastSummary: null,
    error: null,
    nextAction: null,
    selectedChatModel: null,
    searchKeywords: null, 
    identifiedDatasetId: null,
  },
});

// Add nodes
workflow.addNode('llmIntentNode', llmIntentNode as any);
workflow.addNode('searchDatasetsNode', searchDatasetsNode as any);
workflow.addNode('getDatasetDetailsNode', getDatasetDetailsNode as any);

// Define edges
workflow.setEntryPoint('llmIntentNode' as any);

// Conditional edges from llmIntentNode based on its output (nextAction)
workflow.addConditionalEdges(
  'llmIntentNode' as any, 
  (state: CkanAgentState) => {
    console.log(`[CKAN Agent Graph] Routing based on intent: ${state.nextAction}`);
    return state.nextAction || 'END'; // Default to END if nextAction is undefined
  },
  {
    'searchDatasets': 'searchDatasetsNode',
    'getDatasetDetails': 'getDatasetDetailsNode',
    'END': END, 
  } as any // Cast the entire mapping object to any
);

// Edges from action nodes directly to END
workflow.addEdge('searchDatasetsNode' as any, END);
workflow.addEdge('getDatasetDetailsNode' as any, END);

// Compile the graph
export const ckanAgentGraph = workflow.compile();

console.log('[CKAN Agent Graph] Graph compiled successfully');

/*
TODOs:
- Implement summarizeDatasetNode: For summarizing dataset details.
- Implement conditionalBranchNode (using addConditionalEdges): To route based on search results (e.g., one vs. many).
- Implement humanInTheLoopNode: To pause for user feedback/approval. This might involve a custom LangGraph node that can signal the UI.
- Integrate actual tool logic into searchDatasetsNode and getDatasetDetailsNode, including summarization.
- Pass dataStream to nodes: For streaming intermediate results/summaries to the client. This is a key challenge. Options:
    - Make dataStream part of the CkanAgentState (though state should ideally be serializable).
    - Pass it via the `config` argument when invoking the graph if the execution environment allows.
    - Create a custom Runnable/Node class that has access to it.
- Define concrete types for searchResults and datasetDetails in CkanAgentState and channels.
- Wire up the full graph flow as per langgraph-refactor-plan.md.
*/ 