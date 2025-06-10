# Dynamic UI System for Permit Assistant

This document describes the new dynamic UI system that generates user interfaces from JSON schemas provided by the LLM.

## Overview

The dynamic UI system replaces hardcoded UI components with a flexible, schema-driven approach that allows the AI agent to generate custom interfaces based on the data structure and user requirements.

## Architecture

### Core Components

1. **DynamicRecordDetail** - Main container component that renders the complete UI
2. **DynamicSection** - Renders individual sections with fields and actions
3. **DynamicField** - Renders individual form fields with proper formatting
4. **Schema Generator** - Python utility that converts OpenGov records to UI schemas

### Schema Structure

The UI schema follows a hierarchical structure:

```typescript
interface UISchema {
  type: 'detail' | 'table' | 'form';
  header?: UIHeaderSchema;     // Page header with title, metadata
  tabs?: UITabSchema[];        // Tab navigation
  sections?: UISectionSchema[]; // Direct sections (no tabs)
  actions?: UIActionSchema[];   // Global actions
  data: { [key: string]: any }; // The actual data to display
}
```

### Field Types

The system supports various field types with automatic formatting:

- `text` - Plain text display
- `number` - Numeric values
- `date` - Formatted dates
- `currency` - Monetary values with currency symbols
- `textarea` - Multi-line text
- `boolean` - Yes/No badges
- `status` - Colored status badges
- `badge` - Custom styled badges
- `email` - Clickable email links
- `phone` - Formatted phone numbers
- `url` - Clickable links

### Layout Options

Sections can use different layouts:

- `list` - Vertical stack (default)
- `grid` - CSS Grid with configurable columns
- `inline` - Horizontal flex layout

## Usage

### 1. Schema Generation (Python)

```python
from src.agents.permit_assistant.utils.schema_generator import generate_record_detail_schema

# Generate schema from OpenGov record
schema = generate_record_detail_schema(record, community="Newton, MA")
```

### 2. UI Emission (LangGraph)

```python
# In tools_with_ui_node
push_ui_message(
    name="dynamic_record_detail",
    props={
        "schema": ui_schema,
        "community": community
    },
    message=ui_message
)
```

### 3. Component Usage (React)

```tsx
import { DynamicRecordDetail } from './ui';

<DynamicRecordDetail 
  schema={schema}
  community="Newton, MA"
  onAction={(actionId, data) => handleAction(actionId, data)}
/>
```

## Schema Examples

### Basic Field Schema

```json
{
  "key": "estimatedCost",
  "label": "Estimated Project Cost",
  "type": "currency",
  "format": {"currency": "USD"},
  "required": true
}
```

### Section Schema

```json
{
  "title": "Project Information",
  "description": "Details about the construction project",
  "layout": "grid",
  "columns": 3,
  "fields": [...],
  "actions": [
    {
      "id": "edit_project",
      "label": "Edit",
      "type": "link",
      "icon": "✏️"
    }
  ]
}
```

### Tab Schema

```json
{
  "id": "details",
  "label": "Details",
  "count": null,
  "sections": [...],
  "actions": [...]
}
```

## Benefits

1. **Dynamic Content** - UI adapts to data structure automatically
2. **Consistent Styling** - Unified design system across all views
3. **Extensible** - Easy to add new field types and layouts
4. **AI-Driven** - LLM can generate custom schemas for different use cases
5. **Modular** - Reusable components across different workflows

## Migration from Static Components

The system maintains backward compatibility:

- `GetRecordDetail` and `RecordDetail` components still work
- New records use `dynamic_record_detail` UI component
- Fallback to static components if schema generation fails

## Future Enhancements

1. **Form Mode** - Editable fields with validation
2. **Custom Field Types** - File uploads, dropdowns, etc.
3. **Conditional Logic** - Show/hide fields based on values
4. **Real-time Updates** - WebSocket integration for live data
5. **Accessibility** - Enhanced ARIA support and keyboard navigation 