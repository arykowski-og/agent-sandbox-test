import React from 'react';
import { UIFieldSchema } from './types';

interface DynamicFieldProps {
  field: UIFieldSchema;
  value: any;
  onChange?: (value: any) => void;
  readonly?: boolean;
}

const DynamicField: React.FC<DynamicFieldProps> = ({ field, value, onChange, readonly = true }) => {
  const formatValue = (val: any): string => {
    if (val === null || val === undefined) return field.placeholder || 'Not specified';
    
    switch (field.type) {
      case 'date':
        if (!val) return 'Not specified';
        try {
          const date = new Date(val);
          const format = field.format?.dateFormat || 'en-US';
          return date.toLocaleDateString(format, { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit' 
          });
        } catch {
          return String(val);
        }
      
      case 'currency':
        if (!val) return 'Not specified';
        const currency = field.format?.currency || 'USD';
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: currency
        }).format(Number(val) || 0);
      
      case 'boolean':
        return val ? 'Yes' : 'No';
      
      case 'phone':
        if (!val) return 'Not specified';
        // Simple phone formatting
        const cleaned = String(val).replace(/\D/g, '');
        if (cleaned.length === 10) {
          return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
        }
        return String(val);
      
      default:
        return String(val);
    }
  };

  const getFieldStyle = () => {
    const baseStyle: React.CSSProperties = {
      fontSize: '14px',
      color: '#374151',
      lineHeight: '1.4',
      width: field.display?.width || 'auto'
    };

    if (field.display?.color) {
      baseStyle.color = field.display.color;
    }

    return baseStyle;
  };

  const renderField = () => {
    const formattedValue = formatValue(value);

    switch (field.type) {
      case 'status':
        return (
          <span
            style={{
              padding: '4px 12px',
              borderRadius: '16px',
              fontSize: '12px',
              fontWeight: 500,
              color: (() => {
                const status = String(value || '').toLowerCase();
                if (status === 'active' || status === 'approved') return 'white';
                if (status === 'pending') return '#92400e';
                if (status === 'rejected' || status === 'denied') return 'white';
                return 'white';
              })(),
              backgroundColor: (() => {
                const status = String(value || '').toLowerCase();
                if (status === 'active' || status === 'approved') return '#10b981';
                if (status === 'pending') return '#f59e0b';
                if (status === 'rejected' || status === 'denied') return '#ef4444';
                return '#6b7280';
              })(),
              display: 'inline-block',
              textAlign: 'center',
              minWidth: '60px'
            }}
          >
            {formattedValue}
          </span>
        );

      case 'badge':
        return (
          <span
            style={{
              padding: '2px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 500,
              color: field.display?.color || '#374151',
              backgroundColor: field.display?.backgroundColor || '#f3f4f6',
              display: 'inline-block'
            }}
          >
            {field.display?.icon && <span style={{ marginRight: '4px' }}>{field.display.icon}</span>}
            {formattedValue}
          </span>
        );

      case 'boolean':
        const boolValue = Boolean(value);
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

      case 'url':
      case 'email':
        if (!value) return <span style={getFieldStyle()}>{formattedValue}</span>;
        return (
          <a
            href={field.type === 'email' ? `mailto:${value}` : String(value)}
            style={{
              ...getFieldStyle(),
              color: '#2563eb',
              textDecoration: 'none'
            }}
            onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
            onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
          >
            {formattedValue}
            {field.display?.icon && <span style={{ marginLeft: '4px' }}>{field.display.icon}</span>}
          </a>
        );

      default:
        return (
          <span style={getFieldStyle()}>
            {field.display?.icon && <span style={{ marginRight: '4px' }}>{field.display.icon}</span>}
            {field.format?.prefix}{formattedValue}{field.format?.suffix}
          </span>
        );
    }
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{
        display: 'block',
        fontSize: '14px',
        fontWeight: 500,
        color: '#6b7280',
        marginBottom: '4px'
      }}>
        {field.label}
        {field.required && <span style={{ color: '#ef4444', marginLeft: '2px' }}>*</span>}
      </label>
      {renderField()}
    </div>
  );
};

export default DynamicField; 