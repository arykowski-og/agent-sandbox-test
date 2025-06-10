import { Button } from "../ui/button";
import { cn } from "@/lib/utils";

interface SuggestedAction {
  id: string;
  label: string;
  prompt: string;
  icon?: string;
}

interface SuggestedActionsProps {
  onActionClick: (prompt: string) => void;
  className?: string;
}

const SUGGESTED_ACTIONS: SuggestedAction[] = [
  {
    id: "greeting",
    label: "Get Started",
    prompt: "Hello, I need help with permits. What can you do?",
    icon: "👋"
  },
  {
    id: "permit-types",
    label: "Available Permits",
    prompt: "What types of permits exist and how does the process typically work?",
    icon: "📋"
  },
  {
    id: "building-permit",
    label: "Building Permit",
    prompt: "I want to apply for a new building permit in demo. What types are available, what forms do I need to fill out, and what fees should I expect?",
    icon: "🏗️"
  },
  {
    id: "active-permits",
    label: "View Active Permits",
    prompt: "Can you show me all active permit records?",
    icon: "📊"
  },
  {
    id: "permit-search",
    label: "Search Permits",
    prompt: "I need to find all building permits in demo that are currently active, show me their locations, and tell me what inspection steps are required",
    icon: "🔍"
  },
  {
    id: "troubleshooting",
    label: "Need Help?",
    prompt: "I'm having trouble accessing permit information. What should I do?",
    icon: "❓"
  }
];

export function SuggestedActions({ onActionClick, className }: SuggestedActionsProps) {
  return (
    <div className={cn("w-full mb-4", className)}>
      <div className="flex flex-wrap gap-2 justify-center">
        {SUGGESTED_ACTIONS.map((action) => (
          <Button
            key={action.id}
            variant="outline"
            size="sm"
            onClick={() => onActionClick(action.prompt)}
            className="flex items-center gap-2 text-sm bg-white hover:bg-gray-50 border-gray-200 text-gray-700 hover:text-gray-900 transition-colors cursor-pointer"
          >
            {action.icon && <span className="text-base">{action.icon}</span>}
            <span>{action.label}</span>
          </Button>
        ))}
      </div>
    </div>
  );
} 