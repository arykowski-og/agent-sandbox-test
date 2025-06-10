import React, { useState } from 'react';
import { DynamicRecordDetailProps } from './types';
import DynamicSection from './DynamicSection';

const DynamicRecordDetail: React.FC<DynamicRecordDetailProps> = ({ 
  schema, 
  community, 
  onAction 
}) => {
  const [activeTab, setActiveTab] = useState(schema.tabs?.[0]?.id || '');

  const renderHeader = () => {
    if (!schema.header) return null;

    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        padding: '32px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #e1e5e9',
        marginBottom: '24px'
      }}>
        {/* Left side - Title and subtitle */}
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
            {schema.header.title}
          </h1>
          
          {schema.header.subtitle && (
            <p style={{ 
              margin: '0',
              color: '#6b7280',
              fontSize: '16px',
              maxWidth: '400px'
            }}>
              {schema.header.subtitle}
            </p>
          )}
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
          {schema.header.metadata.map((meta, index) => (
            <div key={index} style={{ minWidth: '120px' }}>
              <div style={{ 
                color: '#6b7280', 
                fontSize: '13px', 
                fontWeight: 500, 
                marginBottom: '6px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                {meta.label}
              </div>
              <div style={{ 
                fontSize: '14px', 
                fontWeight: 500,
                color: meta.type === 'link' ? '#4285f4' : '#1f2937',
                display: 'flex',
                alignItems: 'center'
              }}>
                {meta.icon && <span style={{ marginRight: '6px' }}>{meta.icon}</span>}
                {meta.type === 'status' && schema.header?.status ? (
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{ 
                      width: '8px', 
                      height: '8px', 
                      borderRadius: '50%', 
                      backgroundColor: schema.header.status.color,
                      marginRight: '8px' 
                    }} />
                    <span>{schema.header.status.label}</span>
                  </div>
                ) : (
                  meta.value
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTabs = () => {
    if (!schema.tabs || schema.tabs.length === 0) return null;

    return (
      <div style={{ 
        display: 'flex', 
        gap: '32px', 
        marginBottom: '24px',
        borderBottom: '1px solid #e1e5e9',
        paddingLeft: '32px'
      }}>
        {schema.tabs.map((tab) => (
          <div 
            key={tab.id}
            style={{ 
              paddingBottom: '16px', 
              borderBottom: activeTab === tab.id ? '3px solid #4285f4' : 'none',
              cursor: 'pointer'
            }}
            onClick={() => setActiveTab(tab.id)}
          >
            <span style={{ 
              fontWeight: activeTab === tab.id ? 600 : 400,
              color: activeTab === tab.id ? '#4285f4' : '#1f2937',
              fontSize: '16px'
            }}>
              {tab.label}
              {tab.count !== undefined && (
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
    );
  };

  const renderContent = () => {
    // If we have tabs, render the active tab's content
    if (schema.tabs && schema.tabs.length > 0) {
      const activeTabData = schema.tabs.find(tab => tab.id === activeTab);
      if (!activeTabData) return null;

      return (
        <div style={{ 
          padding: '0 24px 24px 24px',
          minHeight: '463px'
        }}>
          {/* Tab Header */}
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '24px'
          }}>
            <h2 style={{ 
              margin: '0',
              fontSize: '24px', 
              fontWeight: 600,
              color: '#1f2937'
            }}>
              {activeTabData.label}
            </h2>
            
            {/* Tab-level actions */}
            {activeTabData.actions && activeTabData.actions.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                {activeTabData.actions.map((action) => (
                  <button
                    key={action.id}
                    onClick={() => onAction?.(action.id, schema.data)}
                    style={{ 
                      border: '1px solid #4285f4',
                      borderRadius: '4px',
                      padding: '8px 16px',
                      backgroundColor: 'white',
                      color: '#4285f4',
                      fontSize: '14px',
                      fontWeight: 500,
                      cursor: 'pointer'
                    }}
                  >
                    {action.icon && <span style={{ marginRight: '6px' }}>{action.icon}</span>}
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Tab Sections */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {activeTabData.sections.map((section, index) => (
              <DynamicSection
                key={index}
                section={section}
                data={schema.data}
                actions={section.actions}
                onAction={onAction}
              />
            ))}
          </div>
        </div>
      );
    }

    // If no tabs, render sections directly
    if (schema.sections && schema.sections.length > 0) {
      return (
        <div style={{ 
          padding: '0 24px 24px 24px',
          minHeight: '400px'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {schema.sections.map((section, index) => (
              <DynamicSection
                key={index}
                section={section}
                data={schema.data}
                actions={section.actions}
                onAction={onAction}
              />
            ))}
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div style={{ 
      maxWidth: '95vw', 
      width: '100%',
      margin: '20px auto', 
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: 'white'
    }}>
      {renderHeader()}
      {renderTabs()}
      {renderContent()}
      
      {/* Global actions */}
      {schema.actions && schema.actions.length > 0 && (
        <div style={{ 
          padding: '24px',
          borderTop: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '12px'
        }}>
          {schema.actions.map((action) => (
            <button
              key={action.id}
              onClick={() => onAction?.(action.id, schema.data)}
              disabled={action.disabled}
              style={{
                padding: '12px 24px',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: 500,
                cursor: action.disabled ? 'not-allowed' : 'pointer',
                border: action.type === 'primary' ? 'none' : '1px solid #d1d5db',
                backgroundColor: (() => {
                  if (action.disabled) return '#f3f4f6';
                  switch (action.type) {
                    case 'primary': return '#2563eb';
                    case 'danger': return '#dc2626';
                    default: return 'white';
                  }
                })(),
                color: (() => {
                  if (action.disabled) return '#9ca3af';
                  switch (action.type) {
                    case 'primary': return 'white';
                    case 'danger': return 'white';
                    default: return '#374151';
                  }
                })(),
                opacity: action.disabled ? 0.6 : 1
              }}
            >
              {action.icon && <span style={{ marginRight: '8px' }}>{action.icon}</span>}
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default DynamicRecordDetail; 