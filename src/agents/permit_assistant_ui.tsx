import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
  Box,
  Card,
  CardContent,
  Divider,
  useTheme,
  alpha
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  LocationOn as LocationIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Business as BusinessIcon,
  Description as DescriptionIcon,
  Phone as PhoneIcon,
  Email as EmailIcon
} from '@mui/icons-material';

// Simple version without Material-UI for testing
interface Record {
  id?: string;
  recordNumber?: string;
  recordType?: string | { name: string; [key: string]: any };
  applicantName?: string;
  dateSubmitted?: string;
  address?: string;
  status?: string;
  createdAt?: string;
  email?: string;
  phone?: string;
  [key: string]: any;
}

interface RecordsTableProps {
  records: Record[];
  community?: string;
}

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

// Individual Record Detail Component
interface RecordDetailProps {
  record: Record;
  community?: string;
}

const RecordDetail: React.FC<RecordDetailProps> = ({ record, community }) => {
  const theme = useTheme();

  const getStatusColor = (status: string): 'success' | 'warning' | 'info' | 'error' | 'default' => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower === 'active' || statusLower === 'approved') return 'success';
    if (statusLower === 'pending') return 'warning';
    if (statusLower === 'in progress' || statusLower === 'processing') return 'info';
    if (statusLower === 'rejected' || statusLower === 'denied') return 'error';
    return 'default';
  };

  const getStatusIcon = (status: string) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower === 'active' || statusLower === 'approved') return <CheckCircleIcon />;
    if (statusLower === 'pending') return <WarningIcon />;
    if (statusLower === 'in progress' || statusLower === 'processing') return <InfoIcon />;
    if (statusLower === 'rejected' || statusLower === 'denied') return <ErrorIcon />;
    return <InfoIcon />;
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'Not specified';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  return (
    <Card sx={{ maxWidth: 800, mx: 'auto', mt: 2, boxShadow: theme.shadows[3] }}>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AssignmentIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
          <Box>
            <Typography variant="h5" component="h2" sx={{ color: 'primary.main', fontWeight: 600 }}>
              {record.recordNumber || record.id || 'Record Details'}
            </Typography>
            {community && (
              <Typography variant="body2" color="text.secondary">
                {community}
              </Typography>
            )}
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Status */}
        {record.status && (
          <Box sx={{ mb: 3 }}>
            <Chip
              icon={getStatusIcon(record.status)}
              label={record.status}
              color={getStatusColor(record.status)}
              variant="filled"
              sx={{ fontWeight: 600, fontSize: '0.875rem' }}
            />
          </Box>
        )}

        {/* Record Details Grid */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          {/* Basic Information */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', color: 'primary.main' }}>
              <InfoIcon sx={{ mr: 1 }} />
              Basic Information
            </Typography>
            
            {record.recordType && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                  Record Type
                </Typography>
                <Typography variant="body1">
                  {typeof record.recordType === 'object' ? record.recordType.name : record.recordType}
                </Typography>
              </Box>
            )}

            {record.dateSubmitted && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                  <CalendarIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  Date Submitted
                </Typography>
                <Typography variant="body1">{formatValue(record.dateSubmitted)}</Typography>
              </Box>
            )}

            {record.createdAt && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                  <CalendarIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  Created At
                </Typography>
                <Typography variant="body1">{formatValue(record.createdAt)}</Typography>
              </Box>
            )}
          </Box>

          {/* Contact & Location Information */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', color: 'primary.main' }}>
              <PersonIcon sx={{ mr: 1 }} />
              Contact & Location
            </Typography>

            {record.applicantName && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                  <PersonIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  Applicant
                </Typography>
                <Typography variant="body1">{formatValue(record.applicantName)}</Typography>
              </Box>
            )}

            {record.address && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                  <LocationIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  Address
                </Typography>
                <Typography variant="body1">{formatValue(record.address)}</Typography>
              </Box>
            )}

            {record.email && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                  <EmailIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  Email
                </Typography>
                <Typography variant="body1">{formatValue(record.email)}</Typography>
              </Box>
            )}

            {record.phone && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, display: 'flex', alignItems: 'center' }}>
                  <PhoneIcon sx={{ fontSize: 16, mr: 0.5 }} />
                  Phone
                </Typography>
                <Typography variant="body1">{formatValue(record.phone)}</Typography>
              </Box>
            )}
          </Box>
        </Box>

        {/* Additional Fields */}
        {Object.keys(record).length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', color: 'primary.main' }}>
              <DescriptionIcon sx={{ mr: 1 }} />
              Additional Details
            </Typography>
            
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
              {Object.entries(record)
                .filter(([key]) => !['recordNumber', 'recordType', 'applicantName', 'dateSubmitted', 'address', 'status', 'createdAt', 'email', 'phone', 'id'].includes(key))
                .map(([key, value]) => (
                  <Box key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                      {key.replace(/([A-Z])/g, ' $1').trim()}
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: typeof value === 'object' ? 'monospace' : 'inherit' }}>
                      {formatValue(value)}
                    </Typography>
                  </Box>
                ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

// Record IDs List Component
interface RecordIdsListProps {
  records: Array<{
    id?: string;
    recordNumber?: string;
    recordType?: string;
    status?: string;
    createdAt?: string;
  }>;
  community?: string;
  total_records?: number;
}

const RecordIdsList: React.FC<RecordIdsListProps> = ({ records, community, total_records }) => {
  const theme = useTheme();

  if (!records || records.length === 0) {
    return (
      <Card sx={{ maxWidth: 600, mx: 'auto', mt: 2 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <AssignmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No records found{community ? ` for ${community}` : ''}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const getStatusColor = (status: string): 'success' | 'warning' | 'info' | 'error' | 'default' => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower === 'active' || statusLower === 'approved') return 'success';
    if (statusLower === 'pending') return 'warning';
    if (statusLower === 'in progress' || statusLower === 'processing') return 'info';
    if (statusLower === 'rejected' || statusLower === 'denied') return 'error';
    return 'default';
  };

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      {/* Header Card */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h5" component="h2" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center',
            color: 'primary.main'
          }}>
            <AssignmentIcon sx={{ mr: 1 }} />
            Available Record IDs{community ? ` for ${community}` : ''}
          </Typography>
          <Divider sx={{ my: 1 }} />
          <Typography variant="body2" color="text.secondary">
            Found {total_records || records.length} record{(total_records || records.length) !== 1 ? 's' : ''}
          </Typography>
        </CardContent>
      </Card>

      {/* Records Grid */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr' }, 
        gap: 2 
      }}>
        {records.map((record, index) => (
          <Card 
            key={record.id || record.recordNumber || index}
            sx={{ 
              transition: 'all 0.2s ease',
              '&:hover': {
                boxShadow: theme.shadows[4],
                transform: 'translateY(-2px)'
              }
            }}
          >
            <CardContent sx={{ p: 2 }}>
              {/* Record Number/ID */}
              <Typography 
                variant="h6" 
                sx={{ 
                  fontFamily: 'monospace',
                  fontWeight: 600,
                  color: 'primary.main',
                  mb: 1,
                  fontSize: '1rem'
                }}
              >
                {record.recordNumber || record.id || `Record ${index + 1}`}
              </Typography>

              {/* Record Type */}
              {record.recordType && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {record.recordType}
                </Typography>
              )}

              {/* Status */}
              {record.status && (
                <Box sx={{ mb: 1 }}>
                  <Chip
                    label={record.status}
                    color={getStatusColor(record.status)}
                    size="small"
                    variant="filled"
                    sx={{ fontSize: '0.75rem' }}
                  />
                </Box>
              )}

              {/* Created Date */}
              {record.createdAt && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                  <CalendarIcon sx={{ fontSize: 12, mr: 0.5 }} />
                  {new Date(record.createdAt).toLocaleDateString()}
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Footer Info */}
      {records.length > 6 && (
        <Box sx={{ 
          mt: 3, 
          p: 2, 
          backgroundColor: alpha(theme.palette.info.main, 0.1),
          borderRadius: 1,
          textAlign: 'center'
        }}>
          <Typography variant="body2" color="text.secondary">
            Showing all {records.length} available records
          </Typography>
        </Box>
      )}
    </Box>
  );
};

// Keep the original Material-UI components but export the simple one for testing
export default {
  records_table: SimpleRecordsTable,
  record_detail: SimpleRecordsTable, // Temporary - using same component
  record_ids_list: SimpleRecordsTable, // Temporary - using same component
}; 