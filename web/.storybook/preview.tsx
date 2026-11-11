import '@fontsource-variable/outfit';
import type { Preview } from '@storybook/react';
import '../src/styles/global.scss';

const preview: Preview = {
  parameters: {
    layout: 'centered',
    backgrounds: { default: 'ledgit', values: [{ name: 'ledgit', value: '#0b0d12' }] },
    a11y: { test: 'error' },
    viewport: {
      viewports: {
        narrow: { name: 'Narrow 360', styles: { width: '360px', height: '740px' } },
      },
    },
  },
};

export default preview;
