import React from 'react';
import './permit_assistant_ui.css';

interface Record {
  id?: string;
  recordNumber?: string;
  recordType?: string;
  applicantName?: string;
  dateSubmitted?: string;
  address?: string;
  status?: string;
  [key: string]: any;
}

interface RecordsTableProps {
  records: Record[];
  community?: string;
}

const RecordsTable: React.FC<RecordsTableProps> = ({ records, community }) => {
  if (!records || records.length === 0) {
    return (
      <div className="no-records">
        <p>No records found{community ? ` for ${community}` : ''}.</p>
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

  // Determine which columns to show based on available data
  const commonFields = [
    { key: 'recordNumber', label: 'Record #' },
    { key: 'recordType', label: 'Record Type' },
    { key: 'applicantName', label: 'Applicant Name' },
    { key: 'dateSubmitted', label: 'Date Submitted' },
    { key: 'address', label: 'Address' },
    { key: 'status', label: 'Status' }
  ];

  // Filter to only show columns that have data in at least one record
  const visibleFields = commonFields.filter(field => 
    records.some(record => record[field.key] !== null && record[field.key] !== undefined)
  );

  return (
    <div className="records-container">
      {community && (
        <div className="records-header">
          <h3 className="records-title">
            Records for {community}
          </h3>
          <p className="records-count">
            Found {records.length} record{records.length !== 1 ? 's' : ''}
          </p>
        </div>
      )}
      
      <div className="records-table-wrapper">
        <table className="records-table min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              {visibleFields.map((field) => (
                <th key={field.key}>
                  {field.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {records.map((record, index) => (
              <tr key={record.id || index}>
                {visibleFields.map((field) => (
                  <td key={field.key}>
                    {field.key === 'status' ? (
                      <span className={`status-badge ${
                        getDisplayValue(record, field.key).toLowerCase() === 'active' 
                          ? 'status-active'
                          : getDisplayValue(record, field.key).toLowerCase() === 'pending'
                          ? 'status-pending'
                          : getDisplayValue(record, field.key).toLowerCase() === 'approved'
                          ? 'status-approved'
                          : getDisplayValue(record, field.key).toLowerCase() === 'rejected'
                          ? 'status-rejected'
                          : 'status-default'
                      }`}>
                        {getDisplayValue(record, field.key)}
                      </span>
                    ) : (
                      <span className={field.key === 'recordNumber' ? 'record-number' : ''}>
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
      
      {records.length > 10 && (
        <div className="records-footer">
          Showing {records.length} records
        </div>
      )}
    </div>
  );
};

export default {
  records_table: RecordsTable,
}; 