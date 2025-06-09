// Re-export all components from the modular UI structure
export {
  SimpleRecordsTable,
  RecordDetail,
  RecordIdsList,
  GetRecordDetail,
  default
} from '../../ui';

// For backward compatibility, also export the types
export type {
  Record,
  RecordsTableProps,
  RecordDetailProps,
  RecordIdsListProps,
  OpenGovRecord,
  GetRecordDetailProps
} from '../../ui'; 