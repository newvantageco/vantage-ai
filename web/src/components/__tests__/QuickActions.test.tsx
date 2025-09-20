import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QuickActions, dashboardActions, searchActions } from '../QuickActions';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Mock toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('QuickActions Component', () => {
  const mockActions = [
    {
      id: 'test-action',
      title: 'Test Action',
      description: 'Test description',
      icon: <div data-testid="test-icon">Test Icon</div>,
      action: jest.fn(),
      variant: 'primary' as const,
      keywords: ['test', 'action'],
    },
  ];

  it('renders with default props', () => {
    render(<QuickActions actions={mockActions} />);
    
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Test Action')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    render(<QuickActions title="Custom Title" actions={mockActions} />);
    
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('handles action clicks', async () => {
    const mockAction = jest.fn();
    const actions = [
      {
        ...mockActions[0],
        action: mockAction,
      },
    ];

    render(<QuickActions actions={actions} />);
    
    const button = screen.getByText('Test Action');
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(mockAction).toHaveBeenCalled();
    });
  });

  it('shows loading state during action execution', async () => {
    const mockAction = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    const actions = [
      {
        ...mockActions[0],
        action: mockAction,
      },
    ];

    render(<QuickActions actions={actions} />);
    
    const button = screen.getByText('Test Action');
    fireEvent.click(button);
    
    // Should show loading spinner
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(mockAction).toHaveBeenCalled();
    });
  });

  it('disables actions when loading', () => {
    const actions = [
      {
        ...mockActions[0],
        loading: true,
      },
    ];

    render(<QuickActions actions={actions} />);
    
    const button = screen.getByText('Test Action');
    expect(button).toBeDisabled();
  });

  it('disables actions when disabled prop is true', () => {
    const actions = [
      {
        ...mockActions[0],
        disabled: true,
      },
    ];

    render(<QuickActions actions={actions} />);
    
    const button = screen.getByText('Test Action');
    expect(button).toBeDisabled();
  });

  it('renders with list layout', () => {
    render(<QuickActions actions={mockActions} layout="list" />);
    
    // In list layout, actions should be full width
    const button = screen.getByText('Test Action');
    expect(button).toHaveClass('w-full');
  });

  it('renders with compact layout', () => {
    render(<QuickActions actions={mockActions} layout="compact" />);
    
    // In compact layout, actions should be in a flex container
    const container = screen.getByText('Test Action').closest('div');
    expect(container).toHaveClass('flex', 'flex-wrap', 'gap-2');
  });

  it('limits actions when maxActions is set', () => {
    const manyActions = Array.from({ length: 10 }, (_, i) => ({
      ...mockActions[0],
      id: `action-${i}`,
      title: `Action ${i}`,
    }));

    render(<QuickActions actions={manyActions} maxActions={5} />);
    
    // Should only render 5 actions
    expect(screen.getAllByRole('button')).toHaveLength(5);
  });

  it('renders badges when provided', () => {
    const actions = [
      {
        ...mockActions[0],
        badge: 'New',
      },
    ];

    render(<QuickActions actions={actions} />);
    
    expect(screen.getByText('New')).toBeInTheDocument();
  });
});

describe('Dashboard Actions', () => {
  it('contains expected actions', () => {
    expect(dashboardActions).toHaveLength(12);
    
    const actionIds = dashboardActions.map(action => action.id);
    expect(actionIds).toContain('create-content');
    expect(actionIds).toContain('schedule-post');
    expect(actionIds).toContain('view-analytics');
    expect(actionIds).toContain('manage-team');
    expect(actionIds).toContain('search-content');
    expect(actionIds).toContain('create-campaign');
    expect(actionIds).toContain('view-reports');
    expect(actionIds).toContain('manage-automation');
    expect(actionIds).toContain('upload-media');
    expect(actionIds).toContain('view-collaboration');
    expect(actionIds).toContain('view-settings');
    expect(actionIds).toContain('export-data');
    expect(actionIds).toContain('import-content');
  });

  it('has proper variants assigned', () => {
    const primaryActions = dashboardActions.filter(action => action.variant === 'primary');
    const secondaryActions = dashboardActions.filter(action => action.variant === 'secondary');
    const tertiaryActions = dashboardActions.filter(action => action.variant === 'tertiary');
    const utilityActions = dashboardActions.filter(action => action.variant === 'utility');

    expect(primaryActions).toHaveLength(4);
    expect(secondaryActions).toHaveLength(3);
    expect(tertiaryActions).toHaveLength(4);
    expect(utilityActions).toHaveLength(2);
  });

  it('has proper keywords for searchability', () => {
    dashboardActions.forEach(action => {
      expect(action.keywords).toBeDefined();
      expect(Array.isArray(action.keywords)).toBe(true);
      expect(action.keywords.length).toBeGreaterThan(0);
    });
  });
});

describe('Search Actions', () => {
  it('contains expected actions', () => {
    expect(searchActions).toHaveLength(9);
    
    const actionIds = searchActions.map(action => action.id);
    expect(actionIds).toContain('create-content');
    expect(actionIds).toContain('copy-urls');
    expect(actionIds).toContain('schedule-content');
    expect(actionIds).toContain('create-campaign');
    expect(actionIds).toContain('analyze-trends');
    expect(actionIds).toContain('share-results');
    expect(actionIds).toContain('favorite-selection');
    expect(actionIds).toContain('export-results');
    expect(actionIds).toContain('clear-selection');
  });

  it('has proper variants assigned', () => {
    const primaryActions = searchActions.filter(action => action.variant === 'primary');
    const secondaryActions = searchActions.filter(action => action.variant === 'secondary');
    const tertiaryActions = searchActions.filter(action => action.variant === 'tertiary');
    const utilityActions = searchActions.filter(action => action.variant === 'utility');

    expect(primaryActions).toHaveLength(2);
    expect(secondaryActions).toHaveLength(2);
    expect(tertiaryActions).toHaveLength(3);
    expect(utilityActions).toHaveLength(2);
  });
});

describe('Action Functionality', () => {
  it('navigates to correct routes', () => {
    const mockPush = jest.fn();
    jest.mocked(require('next/navigation').useRouter).mockReturnValue({
      push: mockPush,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Test dashboard actions
    dashboardActions.forEach(action => {
      if (action.action) {
        action.action();
      }
    });

    // Test search actions
    searchActions.forEach(action => {
      if (action.action) {
        action.action();
      }
    });

    // Verify that actions were called (some may use window.location.href)
    expect(mockPush).toHaveBeenCalled();
  });

  it('shows appropriate toast messages', () => {
    const mockToast = require('react-hot-toast').toast;
    
    // Test dashboard actions
    dashboardActions.forEach(action => {
      if (action.action) {
        action.action();
      }
    });

    // Test search actions
    searchActions.forEach(action => {
      if (action.action) {
        action.action();
      }
    });

    // Verify that toast messages were shown
    expect(mockToast.success).toHaveBeenCalled();
  });
});
