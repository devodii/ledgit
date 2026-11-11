import { useEffect, useState } from 'react';
import { Icon } from '../Icon';
import { IconButton } from '../IconButton';
import styles from './SearchInput.module.scss';

export interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  debounceMs?: number;
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Search',
  label = 'Search claims',
  debounceMs = 300,
}: SearchInputProps) {
  const [draft, setDraft] = useState(value);
  useEffect(() => setDraft(value), [value]);
  useEffect(() => {
    if (draft === value) return;
    const timer = setTimeout(() => onChange(draft), debounceMs);
    return () => clearTimeout(timer);
  }, [draft, value, onChange, debounceMs]);

  return (
    <div className={styles.wrapper} role="search">
      <Icon name="search" size="sm" />
      <input
        className={styles.input}
        type="search"
        aria-label={label}
        placeholder={placeholder}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
      />
      {draft && (
        <IconButton
          icon="x"
          label="Clear search"
          size="sm"
          onClick={() => {
            setDraft('');
            onChange('');
          }}
        />
      )}
    </div>
  );
}
