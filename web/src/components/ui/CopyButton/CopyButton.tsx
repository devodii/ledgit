import { useState } from 'react';
import { IconButton } from '../IconButton';
import { useToast } from '../Toast';

export interface CopyButtonProps {
  value: string;
  label?: string;
}

export function CopyButton({ value, label = 'Copy' }: CopyButtonProps) {
  const toast = useToast();
  const [done, setDone] = useState(false);
  return (
    <IconButton
      icon={done ? 'check' : 'copy'}
      label={done ? 'Copied' : label}
      size="sm"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          setDone(true);
          toast('Copied to clipboard');
          setTimeout(() => setDone(false), 1500);
        } catch {
          toast('Could not copy');
        }
      }}
    />
  );
}
