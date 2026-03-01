// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';
import {format} from 'date-fns';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'UFO/Bigfoot/Missing-411/Supernatural Research',
  tagline: 'UFO research',
  favicon: 'img/favicon.png',

  // Set the production url of your site here
  url: 'https://ouchaku.github.io/',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
    baseUrl: '/ds/',  // Apache の htdoc の directory に相当。この設定でないと local PC の Apache サーバーでは正常動作しない。
    //baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'ouchaku', // Usually your GitHub org/user name.
  projectName: 'ds', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
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
      image: 'img/docusaurus-social-card.jpg',
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
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
            src: 'img/favicon.png', 
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
          copyright: `最新更新：${format(new Date(),'yyyy-MM-dd')}, サイト管理者：横着者, Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
