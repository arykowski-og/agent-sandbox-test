"use client";

import { useStreamContext } from "@/providers/Stream";
import { cn } from "@/lib/utils";

interface ComponentBreadcrumbsProps {
  onNavigateToComponent: (index: number) => void;
  activeComponentIndex?: number;
}

export function ComponentBreadcrumbs({ 
  onNavigateToComponent, 
  activeComponentIndex = 0 
}: ComponentBreadcrumbsProps) {
  const { values } = useStreamContext();
  
  // Get all UI components from the stream
  const allUIComponents = values.ui || [];
  
  // Filter out any UI components that shouldn't be displayed
  const displayableUIComponents = allUIComponents.filter(
    (ui) => ui && ui.metadata?.message_id
  );

  if (!displayableUIComponents.length) {
    return null;
  }

  return (
    <div className="flex flex-col items-center py-4 px-2 h-full">
      <div className="text-xs font-medium text-gray-600 mb-4 text-center">
        Workspace
      </div>
      
      <div className="flex flex-col items-center space-y-6 flex-1">
        {displayableUIComponents.map((component, index) => {
          const isActive = index === activeComponentIndex;
          const isLast = index === displayableUIComponents.length - 1;
          
          // Extract a meaningful name from the component
          const componentName = getComponentDisplayName(component, index);
          
          return (
            <div key={component.id} className="flex flex-col items-center">
              {/* Dot */}
              <button
                onClick={() => onNavigateToComponent(index)}
                className={cn(
                  "w-3 h-3 rounded-full border-2 transition-all duration-200 hover:scale-110 cursor-pointer",
                  isActive 
                    ? "bg-blue-500 border-blue-500 shadow-md" 
                    : "bg-white border-gray-300 hover:border-blue-400"
                )}
                title={componentName}
              />
              
              {/* Label */}
              <div 
                className={cn(
                  "mt-2 text-xs text-center max-w-[80px] leading-tight cursor-pointer transition-colors",
                  isActive 
                    ? "text-blue-600 font-medium" 
                    : "text-gray-500 hover:text-blue-500"
                )}
                onClick={() => onNavigateToComponent(index)}
              >
                {componentName}
              </div>
              
              {/* Vertical line (except for last item) */}
              {!isLast && (
                <div className="w-px h-6 bg-gray-300 mt-2" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Helper function to extract a meaningful display name from the component
function getComponentDisplayName(component: any, index: number): string {
  // Try to extract name from various possible sources
  if (component.metadata?.title) {
    return component.metadata.title;
  }
  
  if (component.metadata?.name) {
    return component.metadata.name;
  }
  
  // Check component name/type for specific UI components
  const componentName = component.name || component.type;
  
  if (componentName) {
    // Handle specific component types with more meaningful labels
    switch (componentName) {
      case 'records_table':
        // For tables, use the same format as the table header: "Active Records (count)"
        const records = component.props?.records;
        const community = component.props?.community;
        if (records && Array.isArray(records)) {
          return `Active Records${community ? ` (${records.length})` : ''}`;
        }
        return 'Table';
        
      case 'dynamic_record_detail':
      case 'get_record':
      case 'record_detail':
        // For detail views, try to get the specific record identifier
        const schema = component.props?.schema;
        const record = component.props?.record;
        
        if (schema?.header?.title) {
          // Use the header title from dynamic schema
          return schema.header.title;
        }
        
        if (record?.attributes?.number) {
          // Use record number for specific record
          return `#${record.attributes.number}`;
        }
        
        if (record?.id) {
          // Fallback to record ID
          return `Record ${record.id.slice(-4)}`;
        }
        
        return 'Details';
        
      case 'record_ids_list':
        return 'List';
        
      default:
        // Convert camelCase or snake_case to readable format
        return componentName
          .replace(/([A-Z])/g, ' $1')
          .replace(/_/g, ' ')
          .replace(/^./, (str: string) => str.toUpperCase())
          .trim();
    }
  }
  
  // Fallback to generic names
  return `View ${index + 1}`;
} 