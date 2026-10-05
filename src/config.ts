import heroImage from './assets/hero-ir.jpg';

export const SITE = {
  website: 'https://cstdl-atmos-snu.github.io/',
  author: 'Daehyun Kim',
  description:
    'Convective Systems/Tropical Dynamics Laboratory at Seoul National University: tropical convection, the Madden-Julian Oscillation, equatorial waves, tropical cyclones, and extreme precipitation.',
  title: 'CSTDL | Seoul National University',
  ogImage: 'astropaper-og.jpg',
  lightAndDarkMode: true,
  postPerPage: 3,
  scheduledPostMargin: 15 * 60 * 1000,

  // Lab Info
  labName: 'Convective Systems/Tropical Dynamics Lab',
  university: 'Seoul National University',
  department: 'School of Earth and Environmental Sciences',
  address: '1 Gwanak-ro, Gwanak-gu, Seoul 08826, Korea',
  logo: '/assets/snu-emblem.svg',
  avatar: '/assets/snu-emblem.svg',
  email: 'daehyun@snu.ac.kr',
  scholar: 'https://tinyurl.com/daehyunkim-publications',
  github: 'https://github.com/cstdl-atmos-snu',

  // Hero Section (Home Page)
  hero: {
    title: 'Tropical convection & large-scale waves',
    subtitle:
      'Understanding what organizes tropical rain-producing systems, improving their prediction, and projecting how they change in a warming world.',
    action: 'View Publications',
    image: heroImage,
    credit: 'Infrared satellite imagery of the global tropics',
  },

  nav: [
    { text: 'Home', link: '/', key: 'home' },
    { text: 'Research', link: '/research', key: 'research' },
    { text: 'Publications', link: '/publications', key: 'publications' },
    { text: 'People', link: '/team', key: 'team' },
    { text: 'News', link: '/news', key: 'news' },
    { text: 'Join Us', link: '/join', key: 'join' },
    { text: 'Search', link: '/search', key: 'search' },
  ],

  customPages: [],

  i18n: {
    enabled: true,
    defaultLocale: 'en',
  },
};

export const LOCALE = {
  lang: 'en',
  langTag: ['en-US'],
} as const;

export const LOGO_IMAGE = {
  enable: true,
  svg: true,
  width: 40,
  height: 40,
};

export const SOCIALS = [
  { link: 'https://github.com/cstdl-atmos-snu', active: true },
];

export const DEFAULT_LANG: 'en' | 'ko' = 'en';
