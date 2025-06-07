# Permit Assistant Generative UI

The Permit Assistant now includes generative UI capabilities that display OpenGov records in a beautiful, interactive table format within the agent-chat-ui.

## Features

### Records Table UI Component

When you use the `get_records` tool through the Permit Assistant, the results are automatically displayed in a responsive table with the following features:

- **Responsive Design**: Works on desktop and mobile devices
- **Smart Column Detection**: Only shows columns that contain data
- **Status Badges**: Color-coded status indicators (Active, Pending, Approved, Rejected)
- **Hover Effects**: Interactive row highlighting
- **Record Count**: Shows total number of records found
- **Community Context**: Displays which community/jurisdiction the records are from

### Supported Data Fields

The table automatically detects and displays these common fields:

- **Record #**: Permit/license number (highlighted in blue)
- **Record Type**: Type of permit or license
- **Applicant Name**: Name of the person/entity applying
- **Date Submitted**: When the application was submitted
- **Address**: Property or business address
- **Status**: Current status with color-coded badges

## How to Use

1. Start a conversation with the Permit Assistant
2. Ask for records from a specific community:
   ```
   "Show me all records for Covington"
   ```
   or
   ```
   "Get records from West Palm Beach"
   ```

3. The assistant will:
   - Call the OpenGov API to fetch records
   - Display a text summary
   - Automatically render a beautiful table below the text

## Technical Implementation

### Files Structure

```
src/agents/
├── permit_assistant.py          # Main agent with UI integration
├── permit_assistant_ui.tsx      # React UI components
└── permit_assistant_ui.css      # Tailwind CSS styles
```

### Configuration

The UI components are configured in `langgraph.json`:

```json
{
  "ui": {
    "permit_assistant": "./src/agents/permit_assistant_ui.tsx"
  }
}
```

### Component Architecture

- **RecordsTable**: Main React component that renders the table
- **Smart Field Detection**: Automatically determines which columns to show
- **Responsive Styling**: Uses Tailwind CSS for modern, responsive design
- **Status Handling**: Special rendering for status fields with color coding

## Customization

### Adding New UI Components

To add more UI components for other tools:

1. Add new components to `permit_assistant_ui.tsx`
2. Export them in the default object
3. Update the agent to emit UI for other tools

### Styling

The component uses Tailwind CSS classes and can be customized by:

1. Modifying `permit_assistant_ui.css`
2. Updating the className props in the React component
3. Adding new CSS classes for custom styling

## Example Usage

**User Input:**
```
"Show me all building permits for Covington"
```

**Agent Response:**
```
I'll get the records for Covington.

Successfully retrieved 12 records for Covington. The records are displayed in the table above.
```

**UI Output:**
A responsive table showing all 12 records with columns for Record #, Record Type, Applicant Name, Date Submitted, Address, and Status.

## Error Handling

- **No Records**: Shows a friendly "No records found" message
- **API Errors**: Displays error messages in the chat
- **UI Errors**: Gracefully falls back to text-only display
- **Missing Data**: Shows "-" for empty fields

## Browser Compatibility

The UI components work in all modern browsers and are optimized for:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile) 