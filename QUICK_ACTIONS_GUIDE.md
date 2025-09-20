# Quick Actions Guide

## Overview

The VANTAGE AI platform now includes comprehensive Quick Actions functionality that provides users with fast access to common tasks and workflows. Quick Actions are implemented across multiple components and can be customized for different contexts.

## Features

### 🚀 Enhanced Functionality
- **Working Actions**: All Quick Actions now have proper functionality with navigation, API calls, and user feedback
- **Loading States**: Visual feedback during action execution with spinners and disabled states
- **Error Handling**: Proper error handling with toast notifications
- **Responsive Design**: Actions adapt to different screen sizes and layouts

### 📱 Multiple Layouts
- **Grid Layout**: Default layout with organized action groups
- **List Layout**: Vertical list for detailed actions with descriptions
- **Compact Layout**: Minimal space usage for quick access

### 🎯 Action Categories
- **Primary Actions**: Main workflow actions (Create Content, Schedule Post, etc.)
- **Secondary Actions**: Supporting actions (Search, Campaigns, etc.)
- **Tertiary Actions**: Quick access actions (Automation, Media, etc.)
- **Utility Actions**: Advanced actions (Export, Import, etc.)

## Components

### 1. QuickActions Component (`web/src/components/QuickActions.tsx`)

A reusable component for displaying Quick Actions with multiple layout options.

```tsx
import { QuickActions, dashboardActions, searchActions } from '@/components/QuickActions';

// Basic usage
<QuickActions 
  title="My Actions"
  actions={dashboardActions}
  layout="grid"
  showDescriptions={true}
  maxActions={8}
/>
```

**Props:**
- `title`: Custom title for the actions section
- `actions`: Array of action objects
- `layout`: 'grid' | 'list' | 'compact'
- `showDescriptions`: Show action descriptions
- `className`: Additional CSS classes
- `maxActions`: Limit number of actions displayed

### 2. QuickActionsTab Component (`web/src/components/QuickActionsTab.tsx`)

A tabbed interface for organizing actions by category.

```tsx
import { QuickActionsTab } from '@/components/QuickActionsTab';

<QuickActionsTab 
  defaultTab="content"
  showCategories={true}
  maxActionsPerTab={12}
/>
```

**Tabs Available:**
- **Content**: Content creation and management
- **Schedule**: Scheduling and publishing
- **Analytics**: Performance metrics and insights
- **Team**: Team management and collaboration
- **Automation**: Workflow automation
- **Media**: Media library and management

### 3. Enhanced Dashboard Actions (`web/src/app/dashboard/page.tsx`)

The main dashboard now includes 12+ Quick Actions organized in tiers:

**Primary Actions (4):**
- Create Content → `/composer`
- Schedule Post → `/calendar?action=schedule`
- View Analytics → `/analytics`
- Manage Team → `/team`

**Secondary Actions (3):**
- Search → `/search`
- Campaign → `/campaigns?action=create`
- Reports → `/reports`

**Tertiary Actions (4):**
- Automation → `/automation`
- Media → `/media?action=upload`
- Collaboration → `/collaboration`
- Settings → `/settings`

**Utility Actions (2):**
- Export Data → Simulated export process
- Import Content → `/content?action=import`

### 4. Enhanced Search Actions (`web/src/app/search/page.tsx`)

The search page includes 9+ Quick Actions for working with search results:

**Primary Actions (2):**
- Create Content → `/composer` with selected results
- Copy URLs → Copy selected URLs to clipboard

**Secondary Actions (2):**
- Schedule → `/calendar` with selected results
- Campaign → `/campaigns` with selected results

**Tertiary Actions (3):**
- Analyze Trends → `/analytics?action=trends`
- Share Results → Native sharing or clipboard
- Favorite Selection → Add to favorites

**Utility Actions (2):**
- Export Results → Download JSON file
- Clear Selection → Clear all selected results

### 5. Enhanced Command Palette (`web/src/components/layout/CommandPalette.tsx`)

The command palette (Cmd/Ctrl+K) now includes 11+ Quick Actions:

**Actions:**
- Create Draft → `/composer`
- Schedule Now → `/calendar?action=schedule`
- Search Content → `/search`
- Create Campaign → `/campaigns?action=create`
- View Analytics → `/analytics`
- Upload Media → `/media?action=upload`
- Manage Team → `/team`
- View Automation → `/automation`
- Export Data → Simulated export
- Go to Inbox → `/collaboration`
- Open Settings → `/settings`

## Action Object Structure

```typescript
interface QuickAction {
  id: string;                    // Unique identifier
  title: string;                 // Display title
  description?: string;          // Optional description
  icon: React.ReactNode;         // Icon component
  action: () => void | Promise<void>; // Action function
  keywords?: string[];           // Search keywords
  variant?: 'primary' | 'secondary' | 'tertiary' | 'utility';
  disabled?: boolean;            // Disabled state
  loading?: boolean;             // Loading state
  badge?: string;                // Optional badge
  color?: string;                // Custom color
  category?: string;             // Action category
}
```

## Usage Examples

### Custom Action Set

```tsx
const customActions = [
  {
    id: 'custom-action',
    title: 'Custom Action',
    description: 'Do something custom',
    icon: <CustomIcon className="h-4 w-4" />,
    action: async () => {
      toast.success('Custom action executed!');
      // Your custom logic here
    },
    variant: 'primary',
    keywords: ['custom', 'action'],
  },
];

<QuickActions 
  title="Custom Actions"
  actions={customActions}
  layout="list"
/>
```

### Tabbed Actions

```tsx
<QuickActionsTab 
  defaultTab="content"
  showCategories={true}
  maxActionsPerTab={8}
  className="my-custom-class"
/>
```

### Grid Layout with Limits

```tsx
<QuickActions 
  actions={dashboardActions}
  layout="grid"
  maxActions={6}
  showDescriptions={false}
/>
```

## Styling

### CSS Classes

The components use Tailwind CSS classes and can be customized:

```css
/* Custom action button styles */
.quick-action-button {
  @apply hover:bg-accent transition-colors;
}

/* Custom loading states */
.quick-action-loading {
  @apply animate-spin;
}

/* Custom hover effects */
.quick-action-hover {
  @apply hover:bg-blue-50 hover:border-blue-300;
}
```

### Theme Integration

Actions automatically adapt to the current theme (light/dark mode) and use the platform's design system.

## Testing

### Unit Tests

Comprehensive unit tests are available in `web/src/components/__tests__/QuickActions.test.tsx`:

```bash
npm test QuickActions.test.tsx
```

### Test Coverage

- Component rendering
- Action execution
- Loading states
- Error handling
- Layout variations
- Action limits
- Badge display

## Performance

### Optimization Features

- **Lazy Loading**: Actions are loaded only when needed
- **Memoization**: Components are memoized to prevent unnecessary re-renders
- **Debounced Actions**: Rapid clicks are debounced to prevent duplicate actions
- **Error Boundaries**: Actions are wrapped in error boundaries for stability

### Best Practices

1. **Keep Actions Simple**: Actions should be quick and focused
2. **Provide Feedback**: Always show loading states and success/error messages
3. **Handle Errors**: Gracefully handle and display errors
4. **Use Appropriate Icons**: Choose clear, recognizable icons
5. **Group Related Actions**: Organize actions logically by category
6. **Limit Actions**: Don't overwhelm users with too many options

## Accessibility

### Features

- **Keyboard Navigation**: All actions are keyboard accessible
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Focus Management**: Clear focus indicators and logical tab order
- **Color Contrast**: Meets WCAG accessibility standards

### Implementation

```tsx
<Button
  aria-label={`${action.title} - ${action.description}`}
  aria-describedby={`action-${action.id}-description`}
  disabled={action.disabled || actionLoading === action.id}
>
  {action.icon}
  <span>{action.title}</span>
</Button>
```

## Future Enhancements

### Planned Features

1. **Custom Action Builder**: UI for creating custom actions
2. **Action Shortcuts**: Keyboard shortcuts for common actions
3. **Action Analytics**: Track action usage and performance
4. **Action Sharing**: Share action sets between users
5. **Action Templates**: Pre-built action sets for common workflows
6. **Action Scheduling**: Schedule actions to run at specific times
7. **Action Automation**: Chain actions together for complex workflows

### Integration Opportunities

1. **API Integration**: Connect actions to external APIs
2. **Webhook Support**: Trigger webhooks from actions
3. **Third-party Services**: Integrate with popular services
4. **Custom Workflows**: Build complex multi-step workflows
5. **Action Marketplace**: Share and discover new actions

## Troubleshooting

### Common Issues

1. **Actions Not Working**: Check that action functions are properly defined
2. **Loading States Not Showing**: Ensure action functions return promises
3. **Navigation Issues**: Verify that routes exist and are accessible
4. **Toast Notifications**: Check that react-hot-toast is properly configured

### Debug Mode

Enable debug mode to see detailed action execution logs:

```tsx
<QuickActions 
  actions={actions}
  debug={true}
/>
```

## Support

For issues or questions about Quick Actions:

1. Check the test files for usage examples
2. Review the component documentation
3. Check the browser console for error messages
4. Verify that all required dependencies are installed

## Changelog

### Version 1.0.0
- Initial implementation of Quick Actions
- Dashboard, Search, and Command Palette integration
- Multiple layout options
- Comprehensive testing
- Accessibility features
- Performance optimizations
