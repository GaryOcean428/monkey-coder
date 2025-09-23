import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/monkey-coder/blog',
    component: ComponentCreator('/monkey-coder/blog', 'cd0'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/archive',
    component: ComponentCreator('/monkey-coder/blog/archive', 'f73'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/authors',
    component: ComponentCreator('/monkey-coder/blog/authors', '07a'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/authors/all-sebastien-lorber-articles',
    component: ComponentCreator('/monkey-coder/blog/authors/all-sebastien-lorber-articles', 'dac'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/authors/yangshun',
    component: ComponentCreator('/monkey-coder/blog/authors/yangshun', '391'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/first-blog-post',
    component: ComponentCreator('/monkey-coder/blog/first-blog-post', '617'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/long-blog-post',
    component: ComponentCreator('/monkey-coder/blog/long-blog-post', '20c'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/mdx-blog-post',
    component: ComponentCreator('/monkey-coder/blog/mdx-blog-post', '185'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/tags',
    component: ComponentCreator('/monkey-coder/blog/tags', '2d1'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/tags/docusaurus',
    component: ComponentCreator('/monkey-coder/blog/tags/docusaurus', 'd95'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/tags/facebook',
    component: ComponentCreator('/monkey-coder/blog/tags/facebook', '81f'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/tags/hello',
    component: ComponentCreator('/monkey-coder/blog/tags/hello', 'd0d'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/tags/hola',
    component: ComponentCreator('/monkey-coder/blog/tags/hola', '02a'),
    exact: true
  },
  {
    path: '/monkey-coder/blog/welcome',
    component: ComponentCreator('/monkey-coder/blog/welcome', '037'),
    exact: true
  },
  {
    path: '/monkey-coder/docs',
    component: ComponentCreator('/monkey-coder/docs', '00f'),
    routes: [
      {
        path: '/monkey-coder/docs',
        component: ComponentCreator('/monkey-coder/docs', '6fa'),
        routes: [
          {
            path: '/monkey-coder/docs',
            component: ComponentCreator('/monkey-coder/docs', '1de'),
            routes: [
              {
                path: '/monkey-coder/docs/',
                component: ComponentCreator('/monkey-coder/docs/', '821'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/',
                component: ComponentCreator('/monkey-coder/docs/', 'e7d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/agent-os-standards',
                component: ComponentCreator('/monkey-coder/docs/agent-os-standards', '25d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/billing',
                component: ComponentCreator('/monkey-coder/docs/billing', 'b49'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/contributing',
                component: ComponentCreator('/monkey-coder/docs/contributing', 'f84'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/migration-guide',
                component: ComponentCreator('/monkey-coder/docs/migration-guide', 'd8c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/openai-response-examples',
                component: ComponentCreator('/monkey-coder/docs/openai-response-examples', 'daa'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/quantum-tasks',
                component: ComponentCreator('/monkey-coder/docs/quantum-tasks', '7f5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/monkey-coder/docs/railpack-docs-links',
                component: ComponentCreator('/monkey-coder/docs/railpack-docs-links', 'f34'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/monkey-coder/',
    component: ComponentCreator('/monkey-coder/', 'd10'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
