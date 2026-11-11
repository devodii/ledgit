import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { Button } from '../Button';
import { Dialog } from './Dialog';

const meta = { title: 'UI/Dialog', component: Dialog } satisfies Meta<typeof Dialog>;
export default meta;
type Story = StoryObj<typeof meta>;

function Demo({ variant }: { variant: 'dialog' | 'drawer' }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button onClick={() => setOpen(true)}>Open {variant}</Button>
      <Dialog
        open={open}
        onOpenChange={setOpen}
        title="How verdicts work"
        description="A verdict is computed from the latest observation of every evidence item."
        variant={variant}
      >
        <p>Nothing here is typed by a person.</p>
      </Dialog>
    </>
  );
}

export const Modal: Story = {
  args: { open: false, onOpenChange: () => {}, title: '', children: null },
  render: () => <Demo variant="dialog" />,
};
export const Drawer: Story = {
  args: { open: false, onOpenChange: () => {}, title: '', children: null },
  render: () => <Demo variant="drawer" />,
};
