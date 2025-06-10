// Export all UI components
export { default as SimpleRecordsTable } from './SimpleRecordsTable';
export { default as RecordDetail } from './RecordDetail';
export { default as RecordIdsList } from './RecordIdsList';
export { default as GetRecordDetail } from './GetRecordDetail';
export { default as DynamicRecordDetail } from './DynamicRecordDetail';
export { default as DynamicField } from './DynamicField';
export { default as DynamicSection } from './DynamicSection';

// Export types
export * from './types';

// Export a default object with all components for backward compatibility
import SimpleRecordsTable from './SimpleRecordsTable';
import RecordDetail from './RecordDetail';
import RecordIdsList from './RecordIdsList';
import GetRecordDetail from './GetRecordDetail';
import DynamicRecordDetail from './DynamicRecordDetail';

export default {
  records_table: SimpleRecordsTable,
  record_detail: RecordDetail,
  record_ids_list: RecordIdsList,
  get_record: GetRecordDetail,
  dynamic_record_detail: DynamicRecordDetail,
}; 