import React, { useState, useMemo } from 'react';
import { RecordsTableProps, Record } from './types';

// Utility function to send message to agent chat UI
const sendMessageToChat = async (message: string) => {
  try {
    // Find the specific textarea with placeholder "Type your message..."
    const chatInput = document.querySelector('textarea[placeholder="Type your message..."]') as HTMLTextAreaElement;
    
    if (chatInput) {
      // Focus the input first
      chatInput.focus();
      
      // Clear the input
      chatInput.value = '';
      
      // Use React's descriptor to set the value properly
      const valueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
      if (valueSetter) {
        valueSetter.call(chatInput, message);
      } else {
        chatInput.value = message;
      }
      
      // Create a proper React SyntheticEvent-like object
      const createSyntheticEvent = (type: string) => {
        const event = new Event(type, { bubbles: true });
        
        // Add React-specific properties
        Object.defineProperty(event, 'target', {
          writable: false,
          value: chatInput
        });
        Object.defineProperty(event, 'currentTarget', {
          writable: false,
          value: chatInput
        });
        
        return event;
      };
      
      // Dispatch input event
      chatInput.dispatchEvent(createSyntheticEvent('input'));
      
      // Try to find and call React's onChange handler directly
      const reactProps = Object.keys(chatInput).find(key => key.startsWith('__reactProps'));
      if (reactProps) {
        const props = (chatInput as any)[reactProps];
        if (props?.onChange) {
          props.onChange({
            target: chatInput,
            currentTarget: chatInput,
            type: 'change'
          });
        }
      }
      
      // Alternative: try to find React fiber
      const reactKeys = Object.keys(chatInput).filter(key => 
        key.startsWith('__reactInternalInstance') || 
        key.startsWith('__reactFiber')
      );
      
      for (const key of reactKeys) {
        const fiber = (chatInput as any)[key];
        if (fiber?.memoizedProps?.onChange) {
          fiber.memoizedProps.onChange({
            target: chatInput,
            currentTarget: chatInput,
            type: 'change'
          });
          break;
        }
      }
      
      console.log('Message populated in chat input:', message);
      
      // Try multiple submission approaches
      const attemptSubmission = () => {
        const submitButton = document.querySelector('button[type="submit"]') as HTMLButtonElement;
        console.log('Submit button found:', !!submitButton);
        console.log('Submit button disabled:', submitButton?.disabled);
        console.log('Submit button text:', submitButton?.textContent);
        
        if (submitButton && submitButton.textContent?.includes('Send')) {
          if (!submitButton.disabled) {
            submitButton.click();
            console.log('✅ Message automatically submitted to LLM:', message);
            return true;
          }
        }
        
        // If button is disabled, try Enter key approach
        console.log('🔄 Trying Enter key submission...');
        const enterEvent = new KeyboardEvent('keydown', {
          key: 'Enter',
          code: 'Enter',
          keyCode: 13,
          which: 13,
          bubbles: true,
          cancelable: true
        });
        
        // Prevent default to avoid new line, then manually trigger form submission
        chatInput.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const form = chatInput.closest('form');
            if (form) {
              // Manually call the form's onSubmit handler
              const formSubmitEvent = new Event('submit', { bubbles: true, cancelable: true });
              form.dispatchEvent(formSubmitEvent);
              console.log('📝 Form submission triggered via Enter key');
            }
          }
        }, { once: true });
        
        chatInput.dispatchEvent(enterEvent);
        return false;
      };
      
      // Try submission with multiple delays
      setTimeout(attemptSubmission, 100);
      setTimeout(attemptSubmission, 300);
      setTimeout(attemptSubmission, 500);
      
    } else {
      console.warn('Chat input not found. Make sure you are on the agent chat UI page.');
      alert(`Chat interface not found. Message: ${message}`);
    }
  } catch (error) {
    console.error('Failed to send message to chat:', error);
    alert(`Failed to send message: ${message}`);
  }
};

const SimpleRecordsTable: React.FC<RecordsTableProps> = ({ records, community, onRecordClick }) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  if (!records || records.length === 0) {
    return (
      <div style={{ 
        maxWidth: '600px', 
        margin: '16px auto', 
        padding: '32px', 
        textAlign: 'center',
        backgroundColor: 'white',
        border: '1px solid #e1e5e9',
        borderRadius: '8px'
      }}>
        <h3 style={{ color: '#374151', fontWeight: 500 }}>No records found{community ? ` for ${community}` : ''}</h3>
      </div>
    );
  }

  // Extract common fields that are likely to be present
  const getDisplayValue = (record: Record, field: string): string => {
    const value = record[field];
    if (value === null || value === undefined) return '-';
    if (typeof value === 'string') return value;
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  // Dynamically determine columns based on actual data
  const generateColumnsFromData = (records: Record[]) => {
    // Priority order for common fields - these will appear first if present (excluding status)
    const priorityFields = [
      { key: 'recordNumber', label: 'Record #', width: '120px' },
      { key: 'recordType', label: 'Record Type', width: '200px' },
      { key: 'dateSubmitted', label: 'Date Submitted', width: '140px' },
      { key: 'applicantName', label: 'Applicant', width: '180px' },
      { key: 'address', label: 'Address', width: '250px' },
    ];

    // Status field configuration - will be added as the last column
    const statusField = { key: 'status', label: 'Status', width: '120px' };

    // Additional fields that might be present - these will appear after priority fields
    const additionalFieldMappings: { [key: string]: { label: string; width: string } } = {
      'projectDescription': { label: 'Project', width: '200px' },
      'applicationName': { label: 'Application', width: '180px' },
      'createdAt': { label: 'Created', width: '140px' },
      'updatedAt': { label: 'Updated', width: '140px' },
      'expiresAt': { label: 'Expires', width: '140px' },
      'submittedAt': { label: 'Submitted', width: '140px' },
      'email': { label: 'Email', width: '200px' },
      'phone': { label: 'Phone', width: '150px' },
      'typeDescription': { label: 'Type Description', width: '200px' },
      'projectID': { label: 'Project ID', width: '120px' },
      'histNumber': { label: 'Hist Number', width: '120px' },
      'renewalNumber': { label: 'Renewal #', width: '120px' },
      'isEnabled': { label: 'Enabled', width: '100px' },
      'submittedOnline': { label: 'Online', width: '100px' },
      'renewalSubmitted': { label: 'Renewal', width: '100px' },
    };

    // Get all unique keys from all records
    const allKeys = new Set<string>();
    records.forEach(record => {
      Object.keys(record).forEach(key => {
        // Skip internal/system fields and status (handled separately)
        if (!['id', 'type', 'attributes', 'relationships', 'status'].includes(key)) {
          allKeys.add(key);
        }
      });
    });

    // Start with priority fields that have data (excluding status)
    const visibleColumns = priorityFields.filter(field => 
      records.some(record => {
        const value = record[field.key];
        return value !== null && value !== undefined && value !== '';
      })
    );

    // Add additional fields that have data and aren't already included
    const priorityKeys = new Set(priorityFields.map(f => f.key));
    Array.from(allKeys).forEach(key => {
      if (!priorityKeys.has(key)) {
        // Check if this field has meaningful data in at least one record
        const hasData = records.some(record => {
          const value = record[key];
          return value !== null && value !== undefined && value !== '';
        });

        if (hasData) {
          const fieldConfig = additionalFieldMappings[key] || {
            label: key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1'),
            width: '150px'
          };
          visibleColumns.push({ key, ...fieldConfig });
        }
      }
    });

    // Always add status column as the last column if it has data
    const hasStatusData = records.some(record => {
      const value = record[statusField.key];
      return value !== null && value !== undefined && value !== '';
    });

    if (hasStatusData) {
      visibleColumns.push(statusField);
    }

    return visibleColumns;
  };

  const visibleFields = generateColumnsFromData(records);

  // Sorting functionality
  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedRecords = useMemo(() => {
    if (!sortConfig) {
      return records;
    }

    return [...records].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      // Handle null/undefined values
      if (aValue === null || aValue === undefined) {
        if (bValue === null || bValue === undefined) return 0;
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      if (bValue === null || bValue === undefined) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }

      // Handle different data types
      let comparison = 0;
      
      // Date fields
      if (sortConfig.key.includes('At') || sortConfig.key.includes('Date') || sortConfig.key === 'dateSubmitted') {
        const aDate = new Date(aValue);
        const bDate = new Date(bValue);
        if (!isNaN(aDate.getTime()) && !isNaN(bDate.getTime())) {
          comparison = aDate.getTime() - bDate.getTime();
        } else {
          comparison = String(aValue).localeCompare(String(bValue));
        }
      }
      // Numeric fields
      else if (typeof aValue === 'number' && typeof bValue === 'number') {
        comparison = aValue - bValue;
      }
      // Boolean fields
      else if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
        comparison = aValue === bValue ? 0 : aValue ? 1 : -1;
      }
      // String fields (default)
      else {
        comparison = String(aValue).localeCompare(String(bValue), undefined, { 
          numeric: true, 
          sensitivity: 'base' 
        });
      }

      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
  }, [records, sortConfig]);

  // Helper function to format field values based on field type
  const formatFieldValue = (record: Record, field: { key: string; label: string; width: string }) => {
    const value = getDisplayValue(record, field.key);
    
    // Special formatting for specific field types
    if (field.key === 'status') {
      return (
        <span
          style={{
            padding: '4px 12px',
            borderRadius: '16px',
            fontSize: '12px',
            fontWeight: 500,
            color: (() => {
              const status = value.toLowerCase();
              if (status === 'complete') return 'white';
              if (status === 'draft') return '#374151';
              if (status === 'stopped') return 'white';
              if (status === 'active') return 'white';
              return 'white';
            })(),
            backgroundColor: (() => {
              const status = value.toLowerCase();
              if (status === 'complete') return '#08a847'; // Green
              if (status === 'draft') return '#dce6f4'; // Light blue-gray
              if (status === 'stopped') return '#f86a0b'; // Orange
              if (status === 'active') return '#5069ff'; // Blue
              return '#3b82f6'; // Default blue
            })(),
            display: 'inline-block',
            textAlign: 'center',
            minWidth: '60px'
          }}
        >
          {value}
        </span>
      );
    }
    
    if (field.key === 'recordNumber') {
      const handleRecordClick = async () => {
        if (value && value !== '-') {
          const message = `I'd like to view record ${value}`;
          
          if (onRecordClick) {
            onRecordClick(value);
          } else {
            // Send message to chat
            await sendMessageToChat(message);
          }
        }
      };

      return (
        <span 
          onClick={handleRecordClick}
          style={{ 
            color: '#2563eb',
            fontWeight: 500,
            fontSize: '14px',
            cursor: 'pointer',
            textDecoration: 'underline',
            textDecorationColor: 'transparent',
            transition: 'text-decoration-color 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.textDecorationColor = '#2563eb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.textDecorationColor = 'transparent';
          }}
        >
          {value}
        </span>
      );
    }

    // Boolean fields
    if (field.key === 'isEnabled' || field.key === 'submittedOnline' || field.key === 'renewalSubmitted') {
      const boolValue = record[field.key];
      if (typeof boolValue === 'boolean') {
        return (
          <span
            style={{
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 500,
              color: boolValue ? '#065f46' : '#7f1d1d',
              backgroundColor: boolValue ? '#d1fae5' : '#fee2e2',
            }}
          >
            {boolValue ? 'Yes' : 'No'}
          </span>
        );
      }
    }

    // Date fields - format dates nicely
    if (field.key.includes('At') || field.key.includes('Date') || field.key === 'dateSubmitted') {
      if (value && value !== '-') {
        try {
          const date = new Date(value);
          if (!isNaN(date.getTime())) {
            return date.toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: '2-digit', 
              day: '2-digit' 
            });
          }
        } catch {
          // Fall through to default formatting
        }
      }
    }

    // Default formatting
    return (
      <span style={{ 
        fontSize: '14px',
        color: '#374151',
        lineHeight: '1.4'
      }}>
        {value}
      </span>
    );
  };

  return (
    <div style={{ width: '100%', marginTop: '20px', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      {/* Header section matching the screenshot */}
      <div style={{ 
        marginBottom: '20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h2 style={{ 
          margin: '0',
          color: '#374151',
          fontSize: '24px',
          fontWeight: 600
        }}>
          Active Records {community && `(${records.length})`}
        </h2>
        <div style={{
          padding: '8px 16px',
          backgroundColor: '#f8fafc',
          border: '1px solid #e1e5e9',
          borderRadius: '6px',
          fontSize: '14px',
          color: '#6b7280',
          cursor: 'pointer'
        }}>
          Actions ▼
        </div>
      </div>
      
      {/* Table matching the screenshot style */}
      <div style={{ 
        backgroundColor: 'white',
        border: '1px solid #e1e5e9',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse'
        }}>
          <thead>
            <tr style={{ 
              backgroundColor: '#f8fafc',
              borderBottom: '1px solid #e1e5e9'
            }}>
              {visibleFields.map((field, index) => (
                <th 
                  key={field.key}
                  onClick={() => handleSort(field.key)}
                  style={{ 
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '14px',
                    width: field.width,
                    borderRight: index < visibleFields.length - 1 ? '1px solid #e1e5e9' : 'none',
                    cursor: 'pointer',
                    userSelect: 'none',
                    transition: 'background-color 0.15s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f1f5f9';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8fafc';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    {field.label}
                    <span style={{ 
                      color: sortConfig?.key === field.key ? '#374151' : '#9ca3af', 
                      fontSize: '12px',
                      fontWeight: sortConfig?.key === field.key ? 'bold' : 'normal'
                    }}>
                      {sortConfig?.key === field.key 
                        ? (sortConfig.direction === 'asc' ? '↑' : '↓')
                        : '⇅'
                      }
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedRecords.map((record, index) => (
              <tr 
                key={record.id || index}
                style={{ 
                  backgroundColor: 'white',
                  borderBottom: index < sortedRecords.length - 1 ? '1px solid #f1f5f9' : 'none',
                  transition: 'background-color 0.15s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8fafc';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'white';
                }}
              >
                {visibleFields.map((field, fieldIndex) => (
                  <td key={field.key} style={{ 
                    padding: '16px',
                    fontSize: '14px',
                    color: '#374151',
                    borderRight: fieldIndex < visibleFields.length - 1 ? '1px solid #f1f5f9' : 'none',
                    verticalAlign: 'middle'
                  }}>
                    {formatFieldValue(record, field)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SimpleRecordsTable; 