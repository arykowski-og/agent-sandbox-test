import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Divider,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { RecordIdsListProps } from './types';

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

export default RecordIdsList; 