import React from 'react';
import { RecordsTableProps, Record } from './types';

const SimpleRecordsTable: React.FC<RecordsTableProps> = ({ records, community }) => {
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
    // Priority order for common fields - these will appear first if present
    const priorityFields = [
      { key: 'recordNumber', label: 'Record #', width: '120px' },
      { key: 'recordType', label: 'Record Type', width: '200px' },
      { key: 'status', label: 'Status', width: '120px' },
      { key: 'dateSubmitted', label: 'Date Submitted', width: '140px' },
      { key: 'applicantName', label: 'Applicant', width: '180px' },
      { key: 'address', label: 'Address', width: '250px' },
    ];

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
        // Skip internal/system fields
        if (!['id', 'type', 'attributes', 'relationships'].includes(key)) {
          allKeys.add(key);
        }
      });
    });

    // Start with priority fields that have data
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

    return visibleColumns;
  };

  const visibleFields = generateColumnsFromData(records);

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
      return (
        <span 
          style={{ 
            color: '#2563eb',
            fontWeight: 500,
            fontSize: '14px'
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
                  style={{ 
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '14px',
                    width: field.width,
                    borderRight: index < visibleFields.length - 1 ? '1px solid #e1e5e9' : 'none',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    {field.label}
                    <span style={{ color: '#9ca3af', fontSize: '12px' }}>⇅</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {records.map((record, index) => (
              <tr 
                key={record.id || index}
                style={{ 
                  backgroundColor: 'white',
                  borderBottom: index < records.length - 1 ? '1px solid #f1f5f9' : 'none',
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