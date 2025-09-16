/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
        'getting-started/first-campaign',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Core Features',
      items: [
        'core-features/content-creation',
        'core-features/scheduling',
        'core-features/analytics',
        'core-features/automation',
        'core-features/collaboration',
      ],
    },
    {
      type: 'category',
      label: 'Integrations',
      items: [
        'integrations/social-media',
        'integrations/email-marketing',
        'integrations/crm',
        'integrations/analytics',
        'integrations/webhooks',
      ],
    },
    {
      type: 'category',
      label: 'AI Features',
      items: [
        'ai-features/content-generation',
        'ai-features/optimization',
        'ai-features/insights',
        'ai-features/translation',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api-reference/authentication',
        'api-reference/endpoints',
        'api-reference/webhooks',
        'api-reference/sdks',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/best-practices',
        'guides/troubleshooting',
        'guides/performance',
        'guides/security',
      ],
    },
    {
      type: 'category',
      label: 'Deployment',
      items: [
        'deployment/docker',
        'deployment/kubernetes',
        'deployment/aws',
        'deployment/monitoring',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/development',
        'contributing/contributing',
        'contributing/code-of-conduct',
      ],
    },
  ],
};

export default sidebars;
