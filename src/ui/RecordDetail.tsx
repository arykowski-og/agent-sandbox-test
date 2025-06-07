import React from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  useTheme,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Edit as EditIcon,
  Link as LinkIcon
} from '@mui/icons-material';
import { RecordDetailProps } from './types';

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

export default RecordDetail; 