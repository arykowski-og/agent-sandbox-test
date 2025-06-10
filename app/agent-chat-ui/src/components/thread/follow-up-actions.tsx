import { Button } from "../ui/button";
import { cn } from "@/lib/utils";

interface FollowUpAction {
  id: string;
  label: string;
  prompt: string;
  icon?: string;
}

interface FollowUpActionsProps {
  followUpActions?: GraphFollowUpAction[];
  onActionClick: (prompt: string) => void;
  className?: string;
}

// This will be populated by the LangGraph post_model_hook
interface GraphFollowUpAction {
  label: string;
  prompt: string;
  category: string;
}

const getCategoryIcon = (category: string): string => {
  const iconMap: { [key: string]: string } = {
    'permit': '📋',
    'inspection': '🔍',
    'application': '📝',
    'status': '📊',
    'document': '📄',
    'fee': '💳',
    'compliance': '⏰',
    'general': '❓'
  };
  return iconMap[category] || '❓';
};



export function FollowUpActions({ followUpActions, onActionClick, className }: FollowUpActionsProps) {
  const actions: FollowUpAction[] = (followUpActions || []).map((action, index) => ({
    id: `followup-${index}`,
    label: action.label,
    prompt: action.prompt,
    icon: getCategoryIcon(action.category)
  }));

  if (actions.length === 0) {
    return null;
  }

  return (
    <div className={cn("w-full mt-4 p-4 bg-gray-50 rounded-lg border", className)}>
      <div className="text-sm font-medium text-gray-700 mb-3">
        What would you like to do next?
      </div>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <Button
            key={action.id}
            variant="outline"
            size="sm"
            onClick={() => onActionClick(action.prompt)}
            className="flex items-center gap-2 text-sm bg-white hover:bg-blue-50 border-gray-200 text-gray-700 hover:text-blue-700 hover:border-blue-300 transition-colors cursor-pointer"
          >
            {action.icon && <span className="text-base">{action.icon}</span>}
            <span>{action.label}</span>
          </Button>
        ))}
      </div>
    </div>
  );
} 