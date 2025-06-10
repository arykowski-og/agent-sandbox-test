import React, { useState } from 'react';
import { UISectionSchema, UIActionSchema } from './types';
import DynamicField from './DynamicField';

interface DynamicSectionProps {
  section: UISectionSchema;
  data: { [key: string]: any };
  actions?: UIActionSchema[];
  onAction?: (actionId: string, data?: any) => void;
  onFieldChange?: (fieldKey: string, value: any) => void;
}

const DynamicSection: React.FC<DynamicSectionProps> = ({ 
  section, 
  data, 
  actions, 
  onAction, 
  onFieldChange 
}) => {
  const [isExpanded, setIsExpanded] = useState(section.defaultExpanded !== false);

  const getLayoutStyle = (): React.CSSProperties => {
    switch (section.layout) {
      case 'grid':
        return {
          display: 'grid',
          gridTemplateColumns: `repeat(${section.columns || 2}, 1fr)`,
          gap: '24px'
        };
      case 'inline':
        return {
          display: 'flex',
          flexWrap: 'wrap',
          gap: '16px',
          alignItems: 'flex-start'
        };
      case 'list':
      default:
        return {
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        };
    }
  };

  const renderActions = () => {
    if (!actions || actions.length === 0) return null;

    return (
      <div style={{ 
        display: 'flex', 
        gap: '12px', 
        marginTop: '16px',
        justifyContent: 'flex-end'
      }}>
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction?.(action.id, data)}
            disabled={action.disabled}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: action.disabled ? 'not-allowed' : 'pointer',
              border: action.type === 'primary' ? 'none' : '1px solid #d1d5db',
              backgroundColor: (() => {
                if (action.disabled) return '#f3f4f6';
                switch (action.type) {
                  case 'primary': return '#2563eb';
                  case 'danger': return '#dc2626';
                  case 'link': return 'transparent';
                  default: return 'white';
                }
              })(),
              color: (() => {
                if (action.disabled) return '#9ca3af';
                switch (action.type) {
                  case 'primary': return 'white';
                  case 'danger': return 'white';
                  case 'link': return '#2563eb';
                  default: return '#374151';
                }
              })(),
              opacity: action.disabled ? 0.6 : 1,
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!action.disabled && action.type !== 'link') {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
              }
            }}
            onMouseLeave={(e) => {
              if (!action.disabled) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            {action.icon && <span style={{ marginRight: '6px' }}>{action.icon}</span>}
            {action.label}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div style={{ 
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      backgroundColor: 'white',
      overflow: 'hidden'
    }}>
      {/* Section Header */}
      <div 
        style={{ 
          padding: '20px 24px',
          borderBottom: section.collapsible ? '1px solid #e5e7eb' : 'none',
          cursor: section.collapsible ? 'pointer' : 'default',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
        onClick={section.collapsible ? () => setIsExpanded(!isExpanded) : undefined}
      >
        <div>
          <h3 style={{ 
            margin: '0 0 4px 0',
            color: '#1f2937',
            fontSize: '18px',
            fontWeight: 600
          }}>
            {section.title}
          </h3>
          {section.description && (
            <p style={{ 
              margin: '0',
              color: '#6b7280',
              fontSize: '14px'
            }}>
              {section.description}
            </p>
          )}
        </div>
        
        {section.collapsible && (
          <span style={{ 
            color: '#6b7280',
            fontSize: '18px',
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease'
          }}>
            ▼
          </span>
        )}
      </div>

      {/* Section Content */}
      {(!section.collapsible || isExpanded) && (
        <div style={{ padding: '24px' }}>
          <div style={getLayoutStyle()}>
            {section.fields.map((field) => (
              <DynamicField
                key={field.key}
                field={field}
                value={data[field.key]}
                onChange={onFieldChange ? (value) => onFieldChange(field.key, value) : undefined}
                readonly={true}
              />
            ))}
          </div>
          {renderActions()}
        </div>
      )}
    </div>
  );
};

export default DynamicSection; 