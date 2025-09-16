import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'VANTAGE AI',
  tagline: 'AI-Powered Marketing Automation Platform',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://docs.vantageai.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config
  organizationName: 'vantage-ai',
  projectName: 'vantage-ai-docs',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/vantage-ai/vantage-ai-docs/tree/main/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/vantage-ai/vantage-ai-docs/tree/main/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/vantage-ai-social-card.jpg',
      navbar: {
        title: 'VANTAGE AI',
        logo: {
          alt: 'VANTAGE AI Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            to: '/api',
            label: 'API Reference',
            position: 'left',
          },
          {
            to: '/blog',
            label: 'Blog',
            position: 'left'
          },
          {
            href: 'https://github.com/vantage-ai/vantage-ai',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'API Reference',
                to: '/api',
              },
              {
                label: 'Guides',
                to: '/docs/guides',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/vantage-ai/vantage-ai',
              },
              {
                label: 'Discord',
                href: 'https://discord.gg/vantage-ai',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/vantage_ai',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'Status',
                href: 'https://status.vantageai.com',
              },
              {
                label: 'Support',
                href: 'https://support.vantageai.com',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} VANTAGE AI. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json', 'yaml'],
      },
      algolia: {
        appId: process.env.ALGOLIA_APP_ID || 'YOUR_APP_ID',
        apiKey: process.env.ALGOLIA_API_KEY || 'YOUR_SEARCH_API_KEY',
        indexName: 'vantage-ai-docs',
        contextualSearch: true,
        searchParameters: {},
        searchPagePath: 'search',
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      announcementBar: {
        id: 'support_us',
        content:
          '⭐️ If you like VANTAGE AI, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/vantage-ai/vantage-ai">GitHub</a> and follow us on <a target="_blank" rel="noopener noreferrer" href="https://twitter.com/vantage_ai">Twitter</a>!',
        backgroundColor: '#fafbfc',
        textColor: '#091E42',
        isCloseable: true,
      },
    }),

  plugins: [
    [
      '@docusaurus/plugin-google-analytics',
      {
        trackingID: process.env.GA_TRACKING_ID || 'G-XXXXXXXXXX',
        anonymizeIP: true,
      },
    ],
    [
      '@docusaurus/plugin-sitemap',
      {
        changefreq: 'weekly',
        priority: 0.5,
        ignorePatterns: ['/tags/**'],
        filename: 'sitemap.xml',
      },
    ],
    [
      '@docusaurus/plugin-ideal-image',
      {
        quality: 70,
        max: 1030,
        min: 640,
        steps: 2,
        disableInDev: false,
      },
    ],
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          {
            from: '/docs/old-page',
            to: '/docs/new-page',
          },
        ],
      },
    ],
  ],

  themes: ['@docusaurus/theme-mermaid', '@docusaurus/theme-live-codeblock'],

  markdown: {
    mermaid: true,
  },
};

export default config;
