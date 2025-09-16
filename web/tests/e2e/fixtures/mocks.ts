import { Page } from '@playwright/test';

export interface MockData {
  oauth: {
    meta: {
      authUrl: string;
      callback: {
        code: string;
        state: string;
        access_token: string;
        user_id: string;
      };
    };
    linkedin: {
      authUrl: string;
      callback: {
        code: string;
        state: string;
        access_token: string;
        user_id: string;
      };
    };
  };
  publishers: {
    meta: {
      pages: Array<{
        id: string;
        name: string;
        access_token: string;
      }>;
      post: {
        id: string;
        success: boolean;
      };
    };
    linkedin: {
      pages: Array<{
        id: string;
        name: string;
        access_token: string;
      }>;
      post: {
        id: string;
        success: boolean;
      };
    };
  };
  insights: {
    meta: {
      metrics: Array<{
        post_id: string;
        impressions: number;
        reach: number;
        likes: number;
        comments: number;
        shares: number;
        clicks: number;
      }>;
    };
    linkedin: {
      metrics: Array<{
        post_id: string;
        impressions: number;
        likes: number;
        comments: number;
        shares: number;
        clicks: number;
      }>;
    };
  };
  content: {
    plans: Array<{
      id: string;
      title: string;
      caption: string;
      hashtags: string[];
      scheduled_at: string;
    }>;
    campaigns: Array<{
      id: string;
      name: string;
      objective: string;
    }>;
  };
}

export const mockData: MockData = {
  oauth: {
    meta: {
      authUrl: 'https://www.facebook.com/v20.0/dialog/oauth?client_id=mock_app_id&redirect_uri=mock_redirect&state=mock_state',
      callback: {
        code: 'mock_meta_code_123',
        state: 'mock_state_123',
        access_token: 'mock_meta_access_token_123',
        user_id: 'mock_meta_user_123'
      }
    },
    linkedin: {
      authUrl: 'https://www.linkedin.com/oauth/v2/authorization?client_id=mock_linkedin_id&redirect_uri=mock_redirect&state=mock_state',
      callback: {
        code: 'mock_linkedin_code_123',
        state: 'mock_state_123',
        access_token: 'mock_linkedin_access_token_123',
        user_id: 'mock_linkedin_user_123'
      }
    }
  },
  publishers: {
    meta: {
      pages: [
        {
          id: 'mock_meta_page_123',
          name: 'Mock Facebook Page',
          access_token: 'mock_meta_page_token_123'
        }
      ],
      post: {
        id: 'mock_meta_post_123',
        success: true
      }
    },
    linkedin: {
      pages: [
        {
          id: 'mock_linkedin_page_123',
          name: 'Mock LinkedIn Page',
          access_token: 'mock_linkedin_page_token_123'
        }
      ],
      post: {
        id: 'mock_linkedin_post_123',
        success: true
      }
    }
  },
  insights: {
    meta: {
      metrics: [
        {
          post_id: 'mock_meta_post_123',
          impressions: 1250,
          reach: 980,
          likes: 45,
          comments: 12,
          shares: 8,
          clicks: 23
        }
      ]
    },
    linkedin: {
      metrics: [
        {
          post_id: 'mock_linkedin_post_123',
          impressions: 890,
          likes: 32,
          comments: 7,
          shares: 5,
          clicks: 18
        }
      ]
    }
  },
  content: {
    plans: [
      {
        id: 'mock_plan_1',
        title: 'Product Launch Announcement',
        caption: 'Exciting news! Our new product is launching soon. Stay tuned for updates!',
        hashtags: ['#productlaunch', '#innovation', '#tech'],
        scheduled_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'mock_plan_2',
        title: 'Behind the Scenes',
        caption: 'Take a look at our development process and team culture.',
        hashtags: ['#behindthescenes', '#team', '#culture'],
        scheduled_at: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString()
      }
    ],
    campaigns: [
      {
        id: 'mock_campaign_1',
        name: 'Q1 Product Launch',
        objective: 'Increase brand awareness and drive product adoption'
      }
    ]
  }
};

export async function setupMocks(page: Page) {
  // Only set up mocks if E2E_MOCKS is enabled
  if (process.env.E2E_MOCKS !== 'true') {
    return;
  }

  // Mock OAuth endpoints
  await page.route('**/api/v1/oauth/meta/init', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        auth_url: mockData.oauth.meta.authUrl
      })
    });
  });

  await page.route('**/api/v1/oauth/meta/callback*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        access_token: mockData.oauth.meta.callback.access_token,
        user_id: mockData.oauth.meta.callback.user_id
      })
    });
  });

  await page.route('**/api/v1/oauth/linkedin/init', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        auth_url: mockData.oauth.linkedin.authUrl
      })
    });
  });

  await page.route('**/api/v1/oauth/linkedin/callback*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        access_token: mockData.oauth.linkedin.callback.access_token,
        user_id: mockData.oauth.linkedin.callback.user_id
      })
    });
  });

  // Mock publisher endpoints
  await page.route('**/api/v1/publishers/meta/pages', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.publishers.meta.pages)
    });
  });

  await page.route('**/api/v1/publishers/linkedin/pages', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.publishers.linkedin.pages)
    });
  });

  await page.route('**/api/v1/publishers/meta/post', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.publishers.meta.post)
    });
  });

  await page.route('**/api/v1/publishers/linkedin/post', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.publishers.linkedin.post)
    });
  });

  // Mock insights endpoints
  await page.route('**/api/v1/insights/meta*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.insights.meta.metrics)
    });
  });

  await page.route('**/api/v1/insights/linkedin*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.insights.linkedin.metrics)
    });
  });

  // Mock content planning endpoints
  await page.route('**/api/v1/content/plan/suggestions*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData.content.plans)
    });
  });

  await page.route('**/api/v1/campaigns*', async route => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockData.content.campaigns)
      });
    } else if (route.request().method() === 'POST') {
      const newCampaign = {
        id: 'mock_campaign_new',
        name: 'New Campaign',
        objective: 'Test objective'
      };
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(newCampaign)
      });
    }
  });

  // Mock schedule endpoints
  await page.route('**/api/v1/schedule/due', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([])
    });
  });

  await page.route('**/api/v1/schedule/bulk', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, created: 1 })
    });
  });

  await page.route('**/api/v1/schedule/run', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ processed: 2, posted: 2, failed: 0 })
    });
  });

  // Mock reports endpoints
  await page.route('**/api/v1/reports/weekly-brief*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        period: '2024-01-01 to 2024-01-07',
        top_performers: [
          {
            post_id: 'mock_post_1',
            caption: 'Top performing post',
            metrics: { impressions: 1500, engagement: 0.08 }
          }
        ],
        recommendations: [
          {
            type: 'timing',
            message: 'Post more content on Tuesday mornings for better engagement'
          }
        ]
      })
    });
  });
}
