import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Monkey Coder',
  tagline: 'AI-powered code generation and analysis platform based on Qwen3-Coder',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  markdown: {
    format: 'detect',
    mermaid: true,
    parseFrontMatter: async (params) => {
      const result = await params.defaultParseFrontMatter(params);
      return result;
    },
  },

  // Set the production url of your site here
  url: 'https://garyocean428.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/monkey-coder/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'GaryOcean428', // Usually your GitHub org/user name.
  projectName: 'monkey-coder', // Usually your repo name.

  onBrokenLinks: 'warn',
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
      {
        docs: {
          sidebarPath: './sidebars.ts',
          exclude: ['**/99-archive/**'],
          remarkPlugins: [],
          rehypePlugins: [],
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/GaryOcean428/monkey-coder/tree/main/docs/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/GaryOcean428/monkey-coder/tree/main/docs/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: ['@docusaurus/theme-live-codeblock'],

  plugins: [
    // Roadmap plugin temporarily disabled - roadmap content migrated to main docs
    // The roadmap MDX files contain angle brackets that cause compilation errors
    // Current roadmap is available at /docs/roadmap.md
    // [
    //   '@docusaurus/plugin-content-docs',
    //   {
    //     id: 'roadmap',
    //     path: 'roadmap',
    //     routeBasePath: 'roadmap',
    //     sidebarPath: require.resolve('./sidebars.roadmap.ts'),
    //     editUrl: 'https://github.com/GaryOcean428/monkey-coder/tree/main/docs/roadmap/',
    //   },
    // ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Monkey Coder',
      logo: {
        alt: 'Monkey Coder Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: 'Docs',
        },
        // Temporarily disabled roadmap link due to disabled roadmap plugin
        // {
        //   type: 'doc',
        //   docId: 'index',
        //   docsPluginId: 'roadmap',
        //   position: 'left',
        //   label: 'Roadmap',
        // },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/GaryOcean428/monkey-coder',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Quick Start',
              to: '/docs/guides/quick-start',
            },
            {
              label: 'Architecture',
              to: '/docs/architecture/agent-os-standards',
            },
            {
              label: 'Deployment',
              to: '/docs/deployment/DEPLOYMENT',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Issues',
              href: 'https://github.com/GaryOcean428/monkey-coder/issues',
            },
            {
              label: 'GitHub Discussions',
              href: 'https://github.com/GaryOcean428/monkey-coder/discussions',
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
              label: 'GitHub',
              href: 'https://github.com/GaryOcean428/monkey-coder',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} GaryOcean428, based on Qwen3-Coder. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    liveCodeBlock: {
      /**
       * The position of the live playground, above or under the editor
       * Possible values: "top" | "bottom"
       */
      playgroundPosition: 'bottom',
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
