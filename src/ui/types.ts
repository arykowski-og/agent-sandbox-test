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