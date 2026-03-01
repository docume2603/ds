// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';
import fs from 'fs';
import path from 'path';
//import {format} from 'date-fns';

const lastUpdatePath = path.resolve(__dirname, 'last_update.text');
let lastUpdateDate = '';

try {
    const data = fs.readFileSync(lastUpdatePath, 'utf8');
    // 日付部分を取得する（先頭10文字）
    lastUpdateDate = data.trim().slice(0, 10);
} catch (err) {
    console.error('Error reading last_update.text file:', err);
}

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'UFO/Bigfoot/Missing-411/Supernatural Research',
  tagline: 'UFO research',
  favicon: 'img/gh_favicon.png',

  // Set the production url of your site here
  // url: 'git@github.com:ume2509/ds.git',
  url: 'https://docume2603.github.io/',
  // Set the /<baseUrl>/ pathname under which your site is served
  // Fo//r GitHub pages deployment, it is often '/<projectName>/'
    baseUrl: '/ds/',  // Apache の htdoc の directory に相当。この設定でないと local PC の Apache サーバーでは正常動作しない。
    //baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'docume2603', // Usually your GitHub org/user name.
  projectName: 'ds', // Usually your repo name.

  onBrokenLinks: 'warn', // 'throw',
  onBrokenMarkdownLinks: 'warn',
  onBrokenAnchors: 'ignore',  // change 2025-06-29, /ds/en/blog で発生してウザいので無視。blog の英語版は用意しないので。
  trailingSlash: false,  // add 2024-07-20
  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "ja",
    locales: ["en", "ja"],
    localeConfigs: {
      en: {
        label: 'English',
      },
      ja: {
        label: '日本語',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
          docs: {
              routeBasePath: '/',
              sidebarPath: './sidebars.js',
              path: 'docs',
            // Please change this to your repo.
        },
          blog: {
              showReadingTime: true,
              blogSidebarTitle: 'Blog 最新記事',
              blogSidebarCount:15,
              tags: 'tags.yml',
              onInlineTags: 'throw',
              //blogSidebarCount:'ALL',
              postsPerPage:1,
              onUntruncatedBlogPosts: 'ignore',
              //truncateMarker: /<!--\s*(more)\s*-->/,
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
      image: 'img/gh_docusaurus-social-card.jpg',
      docs: {
          sidebar: {
              hideable: true,
              autoCollapseCategories: true,
          },
      },
      blog:{
          sidebar:{
              groupByYear:false,
          },
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      navbar: {
          title: '記事一覧',
          logo: {
              alt: 'My Site Logo',
              src: 'img/gh_favicon.png', 
          },
          items:[
              {
                  type: 'localeDropdown',
                  position: 'right',
              },
          {to: '/blog', label: 'Blog', position: 'left'},
          ],
        /*
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'チュートリアル',
          },
          {
            href: 'https://github.com/facebook/docusaurus',
            label: 'GitHub',
            position: 'right',
          },
        ],
        */
      },
      footer: {
        style: 'dark',
        /*
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Top',
                to: '/',
              },
            ],
          },
        ],
        */
          //copyright: `${new Date().getFullYear()} サイト管理者：横着者, Built with Docusaurus.`,
          //copyright: `最新更新：${format(new Date(),'yyyy-MM-dd')}, サイト管理者：横着者, Built with Docusaurus.`,
          copyright: `最新更新：${lastUpdateDate}, サイト管理者：docume2603, Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
