import { type UIMessage } from 'ai';

// To be expanded with more specific fields as the agent develops
// e.g., searchResults, datasetDetails, summaries, etc.
export interface CkanAgentState {
  messages: UIMessage[];
  userInput?: string;
  selectedChatModel?: string; // Added to store the selected chat model ID
  searchResults?: any[]; // Replace 'any' with specific search result type
  datasetDetails?: any; // Replace 'any' with specific dataset detail type
  lastSummary?: string;
  error?: string;
  nextAction?: string; // Added to store the next action determined by llmIntentNode
  searchKeywords?: string; // Added to store keywords extracted by llmIntentNode
  identifiedDatasetId?: string; // Added to store dataset ID extracted by llmIntentNode
  identifiedOrganizationId?: string; // Added for organization details intent
  tagToSearchBy?: string;          // Added for search by tag intent
  // Add other relevant state fields here
} 