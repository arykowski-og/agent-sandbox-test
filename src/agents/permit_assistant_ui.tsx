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
  alpha,
  Button
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
  Email as EmailIcon,
  Edit as EditIcon,
  Link as LinkIcon
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

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'Not specified';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return 'Not specified';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
      });
    } catch {
      return dateString;
    }
  };

  // Extract record data from OpenGov API format
  const attributes = record.attributes || record;
  const recordNumber = attributes.number || record.recordNumber || record.id;
  const recordType = attributes.typeDescription || record.recordType || 'Building Permit';
  const status = attributes.status || record.status;
  const submittedDate = attributes.submittedAt || record.dateSubmitted;
  const expirationDate = attributes.expiresAt;
  const projectId = attributes.projectID;
  const projectDescription = attributes.projectDescription;

  return (
    <Box sx={{ maxWidth: '95vw', width: '100%', mx: 'auto', p: 3, fontFamily: theme.typography.fontFamily }}>
             {/* Header Section */}
       <Box sx={{ 
         display: 'flex', 
         justifyContent: 'space-between', 
         alignItems: 'flex-start',
         mb: 3,
         p: 3,
         backgroundColor: '#f8f9fa',
         borderRadius: 2,
         border: `1px solid ${theme.palette.divider}`
       }}>
        {/* Left side - Record info */}
        <Box>
                     <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
             <LocationIcon sx={{ color: '#6b7280', mr: 1, fontSize: 20 }} />
             <Typography variant="body2" sx={{ color: '#6b7280', fontWeight: 500 }}>
               {community || 'City Hall Square, Newton, MA 02555'}
             </Typography>
           </Box>
          
          <Typography variant="h3" sx={{ 
            fontWeight: 700, 
            fontSize: '2.5rem',
            color: theme.palette.text.primary,
            mb: 1
          }}>
            {recordNumber}
          </Typography>
          
          <Typography variant="body1" sx={{ 
            color: theme.palette.text.secondary,
            fontSize: '1rem'
          }}>
            {recordType}
          </Typography>
        </Box>

                 {/* Right side - Status and metadata */}
         <Box sx={{ textAlign: 'right', minWidth: '60%' }}>
           <Box sx={{ display: 'flex', gap: 6, mb: 2, justifyContent: 'flex-end' }}>
            <Box>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontWeight: 500 }}>
                Applicant
              </Typography>
                             <Typography variant="body2" sx={{ color: '#4285f4', fontWeight: 500 }}>
                 {record.applicantName || 'Sethland Greenlaw'} 
                 <LinkIcon sx={{ fontSize: 14, ml: 0.5 }} />
               </Typography>
            </Box>
            
            <Box>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontWeight: 500 }}>
                Project
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {projectDescription || `Mini-Mall - ${projectId || '1234567'}`}
              </Typography>
                             {projectId && (
                 <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '0.875rem' }}>
                   Edit Project <EditIcon sx={{ fontSize: 12, ml: 0.5 }} />
                 </Typography>
               )}
            </Box>
            
            <Box>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontWeight: 500 }}>
                Expiration Date
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {formatDate(expirationDate) || '11/21/22'} 
                <EditIcon sx={{ fontSize: 14, ml: 0.5 }} />
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontWeight: 500 }}>
                Record Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  bgcolor: status?.toLowerCase() === 'active' ? '#34a853' : '#fbbc04',
                  mr: 1 
                }} />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {status || 'Active'}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Navigation Tabs */}
      <Box sx={{ 
        display: 'flex', 
        gap: 4, 
        mb: 3,
        borderBottom: `1px solid ${theme.palette.divider}`
      }}>
        {[
          { label: 'Details', active: true },
          { label: 'Workflow', count: null },
          { label: 'Attachments', count: 7 },
          { label: 'Location', count: 3 },
          { label: 'Applicant', count: 3 },
          { label: 'Activity', count: null }
        ].map((tab, index) => (
          <Box key={tab.label} sx={{ 
            pb: 2, 
            borderBottom: tab.active ? `3px solid #4285f4` : 'none',
            cursor: 'pointer'
          }}>
            <Typography variant="body1" sx={{ 
              fontWeight: tab.active ? 600 : 400,
              color: tab.active ? '#4285f4' : theme.palette.text.primary,
              display: 'flex',
              alignItems: 'center',
              gap: 0.5
            }}>
              {tab.label}
              {tab.count && (
                <Typography component="span" sx={{ 
                  fontSize: '0.875rem',
                  color: theme.palette.text.secondary 
                }}>
                  {tab.count}
                </Typography>
              )}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Details Section */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, fontSize: '1.5rem' }}>
          Details
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            3 Versions
          </Typography>
          <Box sx={{ 
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 1,
            px: 2,
            py: 0.5
          }}>
            <Typography variant="body2">Current Version ▼</Typography>
          </Box>
          <Button 
            variant="outlined" 
            size="small"
            sx={{ 
              borderColor: '#4285f4',
              color: '#4285f4',
              textTransform: 'none',
              fontWeight: 500
            }}
          >
            Request Changes
          </Button>
        </Box>
      </Box>

      {/* Content Sections */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {/* Project Information Section */}
        <Card sx={{ boxShadow: 'none', border: `1px solid ${theme.palette.divider}` }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Project Information
              </Typography>
              <Button 
                size="small" 
                sx={{ color: '#4285f4', textTransform: 'none' }}
                startIcon={<EditIcon />}
              >
                Edit
              </Button>
            </Box>
            
            <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 3 }}>
              Section level help text or description text
            </Typography>

            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Brief Description of Project
            </Typography>
            
            <Typography variant="body1" sx={{ mb: 4, lineHeight: 1.6 }}>
              Building permit will be for a new build at the intersection of Dean Broadway. 
              This will be a multi-unit building and will be about 8000 square feet.
            </Typography>

                         {/* Project Details Grid */}
             <Box sx={{ 
               display: 'grid', 
               gridTemplateColumns: { xs: '1fr', md: 'repeat(6, 1fr)' }, 
               gap: 4 
             }}>
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Estimated Project Cost
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  $20,000
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Project Type
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  New Construction
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Property Type
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  Commercial
                </Typography>
              </Box>
              
                             <Box>
                 <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                   Build Duration
                 </Typography>
                 <Typography variant="body1" sx={{ fontWeight: 500 }}>
                   90 days
                 </Typography>
               </Box>
               
               <Box>
                 <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                   Submitted Date
                 </Typography>
                 <Typography variant="body1" sx={{ fontWeight: 500 }}>
                   {formatDate(submittedDate) || 'Not specified'}
                 </Typography>
               </Box>
               
               <Box>
                 <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                   Project ID
                 </Typography>
                 <Typography variant="body1" sx={{ fontWeight: 500 }}>
                   {projectId || 'Not assigned'}
                 </Typography>
               </Box>
             </Box>
          </CardContent>
        </Card>

        {/* Contractor Information Section */}
        <Card sx={{ boxShadow: 'none', border: `1px solid ${theme.palette.divider}` }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Contractor Information
              </Typography>
              <Button 
                size="small" 
                sx={{ color: '#4285f4', textTransform: 'none' }}
                startIcon={<EditIcon />}
              >
                Edit
              </Button>
            </Box>

                         {/* Contractor Details Grid */}
             <Box sx={{ 
               display: 'grid', 
               gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' }, 
               gap: 4,
               mb: 3
             }}>
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Contractor Role
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  General
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Type of Work
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  Roofing
                </Typography>
              </Box>
            </Box>

            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Project Description
            </Typography>
            <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.6 }}>
              They're here to take the old shingles off the roof and prep it for the insulation team.
            </Typography>

            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, 
              gap: 3 
            }}>
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Contractor Name
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  Barry Wilkins
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 1 }}>
                  Business Name
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  Barry's Building Construction Business
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
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

// Get Record Detail Component for OpenGov API format
interface OpenGovRecord {
  id: string;
  type: string;
  attributes: {
    number: string;
    histID?: string | null;
    histNumber?: string | null;
    typeID: string;
    typeDescription?: string;
    projectID?: string | null;
    projectDescription?: string | null;
    status: string;
    isEnabled: boolean;
    submittedAt: string;
    expiresAt?: string | null;
    renewalOfRecordID?: string | null;
    renewalNumber?: string | null;
    submittedOnline: boolean;
    renewalSubmitted: boolean;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    updatedBy: string;
  };
  relationships?: {
    applicant?: { links: { related: string } };
    guests?: { links: { related: string } };
    primaryLocation?: { links: { related: string } };
    additionalLocations?: { links: { related: string } };
    workflowSteps?: { links: { related: string } };
    formFields?: { links: { related: string } };
    recordType?: { links: { related: string } };
  };
}

interface GetRecordDetailProps {
  record: OpenGovRecord;
  community?: string;
}

const GetRecordDetail: React.FC<GetRecordDetailProps> = ({ record, community }) => {
  if (!record || !record.attributes) {
    return (
      <div style={{ 
        maxWidth: '800px', 
        margin: '16px auto', 
        padding: '32px', 
        textAlign: 'center',
        backgroundColor: 'white',
        border: '1px solid #e1e5e9',
        borderRadius: '8px'
      }}>
        <h3 style={{ color: '#374151', fontWeight: 500 }}>Record not found</h3>
      </div>
    );
  }

  const { attributes, relationships } = record;

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'Not specified';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status: string): string => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower === 'active') return '#08a847'; // Green
    if (statusLower === 'pending') return '#f59e0b'; // Yellow
    if (statusLower === 'approved') return '#08a847'; // Green
    if (statusLower === 'rejected' || statusLower === 'denied') return '#ef4444'; // Red
    if (statusLower === 'in progress' || statusLower === 'processing') return '#3b82f6'; // Blue
    return '#6b7280'; // Gray default
  };

  const getStatusTextColor = (status: string): string => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower === 'pending') return '#92400e'; // Dark yellow
    return 'white';
  };

  return (
    <div style={{ 
      maxWidth: '95vw', 
      width: '100%',
      margin: '20px auto', 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: 'white'
    }}>
            {/* Header Section */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        padding: '32px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #e1e5e9',
        marginBottom: '0'
      }}>
        {/* Left side - Record info */}
        <div style={{ flex: '0 0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: '#4285f4', marginRight: '8px', fontSize: '14px' }}>📍</span>
            <span style={{ color: '#4285f4', fontWeight: 500, fontSize: '14px' }}>
              {community || 'City Hall Square, Newton, MA 02555'}
            </span>
            <span style={{ color: '#4285f4', marginLeft: '4px', fontSize: '12px' }}>🔗</span>
          </div>
          
          <h1 style={{ 
            margin: '0 0 12px 0',
            color: '#1f2937',
            fontSize: '42px',
            fontWeight: 700,
            lineHeight: 1,
            letterSpacing: '-0.02em'
          }}>
            {attributes.number}
          </h1>
          
          <p style={{ 
            margin: '0',
            color: '#6b7280',
            fontSize: '16px',
            maxWidth: '400px'
          }}>
            {attributes.typeDescription || 'Mixed-Use Building Permit in a Commercial Zone'}
          </p>
        </div>

        {/* Right side - Metadata columns */}
        <div style={{ 
          display: 'flex', 
          gap: '40px', 
          alignItems: 'flex-start',
          flex: '1 1 auto',
          justifyContent: 'flex-end',
          paddingLeft: '40px'
        }}>
          <div style={{ minWidth: '120px' }}>
            <div style={{ 
              color: '#6b7280', 
              fontSize: '13px', 
              fontWeight: 500, 
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Applicant
            </div>
            <div style={{ color: '#4285f4', fontSize: '14px', fontWeight: 500 }}>
              Sethland Greenlaw
            </div>
            <span style={{ color: '#4285f4', fontSize: '12px' }}>🔗</span>
          </div>
          
          <div style={{ minWidth: '140px' }}>
            <div style={{ 
              color: '#6b7280', 
              fontSize: '13px', 
              fontWeight: 500, 
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Project
            </div>
            <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
              {attributes.projectDescription || 'Mini-Mall - 1234567'}
            </div>
            <div style={{ color: '#4285f4', fontSize: '12px', cursor: 'pointer' }}>
              Edit Project ✏️
            </div>
          </div>
          
          <div style={{ minWidth: '120px' }}>
            <div style={{ 
              color: '#6b7280', 
              fontSize: '13px', 
              fontWeight: 500, 
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Expiration Date
            </div>
            <div style={{ fontSize: '14px', fontWeight: 500, display: 'flex', alignItems: 'center' }}>
              {formatDate(attributes.expiresAt || null) || '11/21/22'}
              <span style={{ color: '#6b7280', marginLeft: '6px', fontSize: '12px', cursor: 'pointer' }}>✏️</span>
            </div>
          </div>
          
          <div style={{ minWidth: '100px' }}>
            <div style={{ 
              color: '#6b7280', 
              fontSize: '13px', 
              fontWeight: 500, 
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Record Status
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ 
                width: '8px', 
                height: '8px', 
                borderRadius: '50%', 
                backgroundColor: attributes.status?.toLowerCase() === 'active' ? '#34a853' : '#fbbc04',
                marginRight: '8px' 
              }} />
              <span style={{ fontSize: '14px', fontWeight: 500 }}>
                {attributes.status || 'Active'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ 
        display: 'flex', 
        gap: '32px', 
        marginTop: '24px',
        marginBottom: '24px',
        borderBottom: '1px solid #e1e5e9',
        paddingLeft: '32px'
      }}>
        {[
          { label: 'Details', active: true },
          { label: 'Workflow', count: null },
          { label: 'Attachments', count: 7 },
          { label: 'Location', count: 3 },
          { label: 'Applicant', count: 3 },
          { label: 'Activity', count: null }
        ].map((tab, index) => (
          <div key={tab.label} style={{ 
            paddingBottom: '16px', 
            borderBottom: tab.active ? '3px solid #4285f4' : 'none',
            cursor: 'pointer'
          }}>
            <span style={{ 
              fontWeight: tab.active ? 600 : 400,
              color: tab.active ? '#4285f4' : '#1f2937',
              fontSize: '16px'
            }}>
              {tab.label}
              {tab.count && (
                <span style={{ 
                  fontSize: '14px',
                  color: '#6b7280',
                  marginLeft: '4px'
                }}>
                  {tab.count}
                </span>
              )}
            </span>
          </div>
        ))}
      </div>

      {/* Details Section Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '24px',
        paddingLeft: '24px',
        paddingRight: '24px'
      }}>
        <h2 style={{ 
          margin: '0',
          fontSize: '24px', 
          fontWeight: 600,
          color: '#1f2937'
        }}>
          Details
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#6b7280', fontSize: '14px' }}>
            3 Versions
          </span>
          <div style={{ 
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            padding: '8px 12px',
            fontSize: '14px',
            backgroundColor: 'white'
          }}>
            Current Version ▼
          </div>
          <button style={{ 
            border: '1px solid #4285f4',
            borderRadius: '4px',
            padding: '8px 16px',
            backgroundColor: 'white',
            color: '#4285f4',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer'
          }}>
            Request Changes
          </button>
        </div>
      </div>

      {/* Content Sections */}
      <div style={{ padding: '0 24px 24px 24px' }}>
        {/* Project Information Section */}
        <div style={{ 
          border: '1px solid #e1e5e9',
          borderRadius: '8px',
          marginBottom: '24px',
          backgroundColor: 'white'
        }}>
          <div style={{ padding: '24px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '16px' 
            }}>
              <h3 style={{ 
                margin: '0',
                color: '#1f2937',
                fontSize: '18px',
                fontWeight: 600
              }}>
                Project Information
              </h3>
              <button style={{ 
                background: 'none',
                border: 'none',
                color: '#4285f4',
                fontSize: '14px',
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                ✏️ Edit
              </button>
            </div>
            
            <p style={{ 
              margin: '0 0 24px 0',
              color: '#6b7280',
              fontSize: '14px'
            }}>
              Section level help text or description text
            </p>

            <h4 style={{ 
              margin: '0 0 12px 0',
              color: '#1f2937',
              fontSize: '16px',
              fontWeight: 600
            }}>
              Brief Description of Project
            </h4>
            
            <p style={{ 
              margin: '0 0 32px 0',
              color: '#1f2937',
              fontSize: '14px',
              lineHeight: 1.6
            }}>
              Building permit will be for a new build at the intersection of Dean Broadway. 
              This will be a multi-unit building and will be about 8000 square feet.
            </p>

            {/* Project Details Grid */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '24px' 
            }}>
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Estimated Project Cost
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  $20,000
                </div>
              </div>
              
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Project Type
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  New Construction
                </div>
              </div>
              
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Property Type
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  Commercial
                </div>
              </div>
              
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Build Duration
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  90 days
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Contractor Information Section */}
        <div style={{ 
          border: '1px solid #e1e5e9',
          borderRadius: '8px',
          marginBottom: '24px',
          backgroundColor: 'white'
        }}>
          <div style={{ padding: '24px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '24px' 
            }}>
              <h3 style={{ 
                margin: '0',
                color: '#1f2937',
                fontSize: '18px',
                fontWeight: 600
              }}>
                Contractor Information
              </h3>
              <button style={{ 
                background: 'none',
                border: 'none',
                color: '#4285f4',
                fontSize: '14px',
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                ✏️ Edit
              </button>
            </div>

            {/* Contractor Details Grid */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '24px',
              marginBottom: '24px'
            }}>
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Contractor Role
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  General
                </div>
              </div>
              
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Type of Work
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  Roofing
                </div>
              </div>
            </div>

            <h4 style={{ 
              margin: '0 0 12px 0',
              color: '#1f2937',
              fontSize: '16px',
              fontWeight: 600
            }}>
              Project Description
            </h4>
            <p style={{ 
              margin: '0 0 24px 0',
              color: '#1f2937',
              fontSize: '14px',
              lineHeight: 1.6
            }}>
              They're here to take the old shingles off the roof and prep it for the insulation team.
            </p>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '24px' 
            }}>
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Contractor Name
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  Barry Wilkins
                </div>
              </div>
              
              <div>
                <div style={{ color: '#6b7280', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                  Business Name
                </div>
                <div style={{ color: '#1f2937', fontSize: '14px', fontWeight: 500 }}>
                  Barry's Building Construction Business
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Record Information Section */}
        <div style={{ 
          border: '1px solid #e1e5e9',
          borderRadius: '8px',
          marginBottom: '24px',
          backgroundColor: 'white'
        }}>
          <div style={{ padding: '24px' }}>
            <h3 style={{ 
              margin: '0 0 24px 0',
              color: '#1f2937',
              fontSize: '18px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center'
            }}>
              <span style={{ marginRight: '8px' }}>ℹ️</span>
              Record Information
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6b7280',
                  marginBottom: '4px'
                }}>
                  Record ID
                </label>
                <span style={{ 
                  fontSize: '16px',
                  color: '#1f2937',
                  fontFamily: 'monospace',
                  backgroundColor: '#f3f4f6',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  {record.id}
                </span>
              </div>

              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6b7280',
                  marginBottom: '4px'
                }}>
                  Type ID
                </label>
                <span style={{ fontSize: '16px', color: '#1f2937' }}>
                  {attributes.typeID}
                </span>
              </div>

              {attributes.typeDescription && (
                <div>
                  <label style={{ 
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#6b7280',
                    marginBottom: '4px'
                  }}>
                    Type Description
                  </label>
                  <span style={{ fontSize: '16px', color: '#1f2937' }}>
                    {attributes.typeDescription}
                  </span>
                </div>
              )}

              {attributes.projectID && (
                <div>
                  <label style={{ 
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#6b7280',
                    marginBottom: '4px'
                  }}>
                    Project ID
                  </label>
                  <span style={{ fontSize: '16px', color: '#1f2937' }}>
                    {attributes.projectID}
                  </span>
                </div>
              )}

              {attributes.projectDescription && (
                <div>
                  <label style={{ 
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#6b7280',
                    marginBottom: '4px'
                  }}>
                    Project Description
                  </label>
                  <span style={{ fontSize: '16px', color: '#1f2937' }}>
                    {attributes.projectDescription}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Dates & Timeline */}
          <div>
            <h3 style={{ 
              margin: '0 0 20px 0',
              color: '#1f2937',
              fontSize: '18px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center'
            }}>
              <span style={{ marginRight: '8px' }}>📅</span>
              Timeline
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6b7280',
                  marginBottom: '4px'
                }}>
                  Created At
                </label>
                <span style={{ fontSize: '16px', color: '#1f2937' }}>
                  {formatDate(attributes.createdAt)}
                </span>
              </div>

              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6b7280',
                  marginBottom: '4px'
                }}>
                  Submitted At
                </label>
                <span style={{ fontSize: '16px', color: '#1f2937' }}>
                  {formatDate(attributes.submittedAt)}
                </span>
              </div>

              {attributes.updatedAt && (
                <div>
                  <label style={{ 
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#6b7280',
                    marginBottom: '4px'
                  }}>
                    Last Updated
                  </label>
                  <span style={{ fontSize: '16px', color: '#1f2937' }}>
                    {formatDate(attributes.updatedAt)}
                  </span>
                </div>
              )}

              {attributes.expiresAt && (
                <div>
                  <label style={{ 
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: 500,
                    color: '#6b7280',
                    marginBottom: '4px'
                  }}>
                    Expires At
                  </label>
                  <span style={{ fontSize: '16px', color: '#1f2937' }}>
                    {formatDate(attributes.expiresAt)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Submission Details */}
        <div style={{ 
          backgroundColor: '#f8fafc',
          padding: '24px',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <h3 style={{ 
            margin: '0 0 16px 0',
            color: '#1f2937',
            fontSize: '18px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center'
          }}>
            <span style={{ marginRight: '8px' }}>📝</span>
            Submission Details
          </h3>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px'
          }}>
            <div>
              <label style={{ 
                display: 'block',
                fontSize: '14px',
                fontWeight: 500,
                color: '#6b7280',
                marginBottom: '4px'
              }}>
                Submitted Online
              </label>
              <span style={{ 
                fontSize: '16px', 
                color: attributes.submittedOnline ? '#059669' : '#dc2626',
                fontWeight: 500
              }}>
                {attributes.submittedOnline ? 'Yes' : 'No'}
              </span>
            </div>

            <div>
              <label style={{ 
                display: 'block',
                fontSize: '14px',
                fontWeight: 500,
                color: '#6b7280',
                marginBottom: '4px'
              }}>
                Renewal Submitted
              </label>
              <span style={{ 
                fontSize: '16px', 
                color: attributes.renewalSubmitted ? '#059669' : '#dc2626',
                fontWeight: 500
              }}>
                {attributes.renewalSubmitted ? 'Yes' : 'No'}
              </span>
            </div>

            {attributes.renewalOfRecordID && (
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6b7280',
                  marginBottom: '4px'
                }}>
                  Renewal of Record
                </label>
                <span style={{ 
                  fontSize: '16px',
                  color: '#1f2937',
                  fontFamily: 'monospace'
                }}>
                  {attributes.renewalOfRecordID}
                </span>
              </div>
            )}

            {attributes.renewalNumber && (
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6b7280',
                  marginBottom: '4px'
                }}>
                  Renewal Number
                </label>
                <span style={{ fontSize: '16px', color: '#1f2937' }}>
                  {attributes.renewalNumber}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Related Resources */}
        {relationships && Object.keys(relationships).length > 0 && (
          <div>
            <h3 style={{ 
              margin: '0 0 16px 0',
              color: '#1f2937',
              fontSize: '18px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center'
            }}>
              <span style={{ marginRight: '8px' }}>🔗</span>
              Related Resources
            </h3>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '12px'
            }}>
              {Object.entries(relationships).map(([key, value]) => (
                <div key={key} style={{
                  padding: '12px 16px',
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ 
                    fontSize: '14px',
                    color: '#374151',
                    fontWeight: 500,
                    textTransform: 'capitalize'
                  }}>
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <span style={{ 
                    fontSize: '12px',
                    color: '#6b7280',
                    backgroundColor: '#f3f4f6',
                    padding: '2px 6px',
                    borderRadius: '4px'
                  }}>
                    Available
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Information */}
        <div style={{ 
          marginTop: '24px',
          paddingTop: '24px',
          borderTop: '1px solid #e5e7eb'
        }}>
          <h4 style={{ 
            margin: '0 0 12px 0',
            color: '#6b7280',
            fontSize: '14px',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            System Information
          </h4>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '12px',
            fontSize: '12px',
            color: '#6b7280'
          }}>
            <div>Created by: {attributes.createdBy}</div>
            <div>Updated by: {attributes.updatedBy}</div>
            {attributes.histID && <div>History ID: {attributes.histID}</div>}
            {attributes.histNumber && <div>History Number: {attributes.histNumber}</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

// Keep the original Material-UI components but export the simple one for testing
export default {
  records_table: SimpleRecordsTable,
  record_detail: SimpleRecordsTable, // Temporary - using same component
  record_ids_list: SimpleRecordsTable, // Temporary - using same component
  get_record: GetRecordDetail, // New component for individual record details
}; 