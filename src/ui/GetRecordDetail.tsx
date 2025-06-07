import React from 'react';
import { GetRecordDetailProps } from './types';

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

export default GetRecordDetail; 