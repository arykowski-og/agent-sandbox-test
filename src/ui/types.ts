// Shared types for permit assistant UI components

export interface Record {
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

export interface RecordsTableProps {
  records: Record[];
  community?: string;
  onRecordClick?: (recordId: string) => void;
}

export interface RecordDetailProps {
  record: Record;
  community?: string;
}

export interface RecordIdsListProps {
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

export interface OpenGovRecord {
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

export interface GetRecordDetailProps {
  record: OpenGovRecord;
  community?: string;
}

// Dynamic UI Schema Types
export interface UIFieldSchema {
  key: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'currency' | 'textarea' | 'dropdown' | 'file' | 'boolean' | 'email' | 'phone' | 'url' | 'status' | 'badge';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  format?: {
    prefix?: string;
    suffix?: string;
    dateFormat?: string;
    currency?: string;
  };
  display?: {
    width?: string;
    color?: string;
    backgroundColor?: string;
    icon?: string;
  };
}

export interface UISectionSchema {
  title: string;
  description?: string;
  fields: UIFieldSchema[];
  layout?: 'grid' | 'list' | 'inline';
  columns?: number;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  actions?: UIActionSchema[];
}

export interface UITabSchema {
  id: string;
  label: string;
  count?: number;
  sections: UISectionSchema[];
  actions?: UIActionSchema[];
}

export interface UIActionSchema {
  id: string;
  label: string;
  type: 'primary' | 'secondary' | 'danger' | 'link';
  icon?: string;
  disabled?: boolean;
  confirmation?: {
    title: string;
    message: string;
  };
}

export interface UIHeaderSchema {
  title: string;
  subtitle?: string;
  status?: {
    label: string;
    color: string;
    icon?: string;
  };
  metadata: Array<{
    label: string;
    value: string;
    type?: 'text' | 'link' | 'date' | 'badge' | 'status';
    icon?: string;
  }>;
  actions?: UIActionSchema[];
}

export interface UISchema {
  type: 'detail' | 'table' | 'form';
  header?: UIHeaderSchema;
  tabs?: UITabSchema[];
  sections?: UISectionSchema[];
  actions?: UIActionSchema[];
  data: { [key: string]: any };
}

export interface DynamicUIProps {
  schema: UISchema;
  onAction?: (actionId: string, data?: any) => void;
  onFieldChange?: (fieldKey: string, value: any) => void;
}

export interface DynamicRecordDetailProps {
  schema: UISchema;
  community?: string;
  onAction?: (actionId: string, data?: any) => void;
} 