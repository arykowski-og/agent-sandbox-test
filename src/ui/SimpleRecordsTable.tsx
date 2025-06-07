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

  // Define columns in the exact order from the screenshot
  const commonFields = [
    { key: 'recordNumber', label: 'Record #', width: '120px' },
    { key: 'recordType', label: 'Record Type', width: '200px' },
    { key: 'dateSubmitted', label: 'Date Submitted', width: '140px' },
    { key: 'status', label: 'Record Status', width: '120px' }
  ];

  // Filter to only show columns that have data in at least one record
  const visibleFields = commonFields.filter(field => 
    records.some(record => record[field.key] !== null && record[field.key] !== undefined)
  );

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
                    {field.key === 'status' ? (
                      <span
                        style={{
                          padding: '4px 12px',
                          borderRadius: '16px',
                          fontSize: '12px',
                          fontWeight: 500,
                          color: (() => {
                            const status = getDisplayValue(record, field.key).toLowerCase();
                            if (status === 'complete') return 'white';
                            if (status === 'draft') return '#374151';
                            if (status === 'stopped') return 'white';
                            if (status === 'active') return 'white';
                            return 'white';
                          })(),
                          backgroundColor: (() => {
                            const status = getDisplayValue(record, field.key).toLowerCase();
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
                        {getDisplayValue(record, field.key)}
                      </span>
                    ) : field.key === 'recordNumber' ? (
                      <span 
                        style={{ 
                          color: '#2563eb',
                          fontWeight: 500,
                          fontSize: '14px'
                        }}
                      >
                        {getDisplayValue(record, field.key)}
                      </span>
                    ) : (
                      <span style={{ 
                        fontSize: '14px',
                        color: '#374151',
                        lineHeight: '1.4'
                      }}>
                        {getDisplayValue(record, field.key)}
                      </span>
                    )}
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