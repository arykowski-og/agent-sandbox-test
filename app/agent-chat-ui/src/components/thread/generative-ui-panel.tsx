"use client";

import { Fragment, useEffect, useRef } from "react";
import { useStreamContext } from "@/providers/Stream";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";
import { useArtifact } from "./artifact";
import { useQueryState } from "nuqs";
import { OpenDataIcon } from "../icons/open-data";
import { PermitAssistantIcon } from "../icons/permit-assistant";
import { FinancialAssistantIcon } from "../icons/financial-assistant";
import { BudgetIcon } from "../icons/budget";
import { CitizenIcon } from "../icons/citizen";

// Agent data from landing page
const agents = [
  {
    id: "open_data_agent",
    name: "Open Data Agent",
    description: "Search and analyze open government datasets through CKAN data portals. Find public data for research and analysis.",
    icon: <OpenDataIcon size={32} />,
  },
  {
    id: "permit_assistant",
    name: "Permit Processing Assistant",
    description: "Streamline permit applications by auto-checking compliance requirements and flagging incomplete submissions.",
    icon: <PermitAssistantIcon size={32} />,
  },
  {
    id: "finance_assistant",
    name: "Finance Assistant",
    description: "AI-powered financial data analysis using OpenGov FIN GraphQL API. Query budgets, expenditures, revenues, and generate insights.",
    icon: <FinancialAssistantIcon size={32} />,
  },
  {
    id: "budget_analyzer",
    name: "Budget Analyzer Pro",
    description: "Automatically analyze budget variances, identify spending patterns, and generate comprehensive reports.",
    icon: <BudgetIcon size={32} />,
  },
  {
    id: "citizen_query",
    name: "Citizen Query Bot",
    description: "Handle common citizen inquiries 24/7, provide instant answers about services, and route complex issues.",
    icon: <CitizenIcon size={32} />,
  },
  {
    id: "agent",
    name: "General Assistant",
    description: "A versatile AI assistant ready to help with various tasks and questions.",
    icon: "🤖",
  },
];

export function GenerativeUIPanel() {
  const stream = useStreamContext();
  const artifact = useArtifact();
  const { values } = useStreamContext();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prevComponentCountRef = useRef(0);
  
  // Get the current assistant ID from URL parameters or stream context
  const [assistantAlias] = useQueryState("assistant");
  const assistantId = stream.configuredAssistantId || assistantAlias;
  
  // Find the current agent data
  const currentAgent = agents.find(agent => agent.id === assistantId) || {
    name: "AI Assistant",
    description: "Interactive AI assistant ready to help with your tasks.",
    icon: "🤖"
  };

  // Get all UI components from the stream
  const allUIComponents = values.ui || [];

  // Filter out any UI components that shouldn't be displayed
  const displayableUIComponents = allUIComponents.filter(
    (ui) => ui && ui.metadata?.message_id
  );

  // Auto-scroll to new components when they're added
  useEffect(() => {
    const currentCount = displayableUIComponents.length;
    const prevCount = prevComponentCountRef.current;
    
    // If we have new components, scroll to the top of the newest component
    if (currentCount > prevCount && currentCount > 0) {
      const scrollContainer = scrollContainerRef.current;
      if (scrollContainer) {
        // Use a small delay to ensure the new component is rendered
        setTimeout(() => {
          // Find the newest component (last one in the list)
          const newestComponentElement = scrollContainer.querySelector(`[data-component-index="${currentCount - 1}"]`);
          if (newestComponentElement) {
            // Scroll so the top of the new component is at the top of the visible area
            const containerRect = scrollContainer.getBoundingClientRect();
            const componentRect = newestComponentElement.getBoundingClientRect();
            const scrollTop = scrollContainer.scrollTop + (componentRect.top - containerRect.top);
            
            scrollContainer.scrollTo({
              top: scrollTop,
              behavior: 'smooth'
            });
          } else {
            // Fallback: scroll to bottom if we can't find the specific component
            scrollContainer.scrollTo({
              top: scrollContainer.scrollHeight,
              behavior: 'smooth'
            });
          }
        }, 100);
      }
    }
    
    // Update the previous count
    prevComponentCountRef.current = currentCount;
  }, [displayableUIComponents.length]);

  if (!displayableUIComponents.length) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center text-gray-500">
          <div className="mb-4 flex justify-center">
            {typeof currentAgent.icon === 'string' ? (
              <span className="text-4xl">{currentAgent.icon}</span>
            ) : (
              <div className="scale-150">{currentAgent.icon}</div>
            )}
          </div>
          <div className="mb-2 text-lg font-medium">{currentAgent.name}</div>
          <div className="text-sm max-w-md">
            {currentAgent.description}
          </div>
          <div className="mt-4 text-xs text-gray-400">
            Interactive components generated by this assistant will appear here
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={scrollContainerRef}
      className="h-full overflow-y-auto p-4"
    >
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          {typeof currentAgent.icon === 'string' ? (
            <span className="text-xl">{currentAgent.icon}</span>
          ) : (
            <div className="scale-75">{currentAgent.icon}</div>
          )}
          <h2 className="text-lg font-semibold text-gray-800">
            {currentAgent.name}
          </h2>
        </div>
        <p className="text-sm text-gray-600">
          Interactive components from your conversation
        </p>
      </div>
      
      <div className="space-y-4">
        {displayableUIComponents.map((uiComponent, index) => (
          <div
            key={uiComponent.id}
            data-component-index={index}
            className="rounded-lg border bg-white p-4 shadow-sm"
          >
            <LoadExternalComponent
              stream={stream}
              message={uiComponent}
              meta={{ ui: uiComponent, artifact }}
            />
          </div>
        ))}
      </div>
    </div>
  );
} 