import * as RadixSelect from '@radix-ui/react-select';
import { Icon } from '../Icon';
import styles from './Select.module.scss';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
}

const ALL = '__all__';

export function Select({ label, value, onChange, options }: SelectProps) {
  return (
    <RadixSelect.Root value={value || ALL} onValueChange={(v) => onChange(v === ALL ? '' : v)}>
      <RadixSelect.Trigger className={styles.trigger} aria-label={label}>
        <RadixSelect.Value />
        <RadixSelect.Icon>
          <Icon name="chevron-down" size="sm" />
        </RadixSelect.Icon>
      </RadixSelect.Trigger>
      <RadixSelect.Portal>
        <RadixSelect.Content className={styles.content} position="popper" sideOffset={6}>
          <RadixSelect.Viewport>
            {[{ value: ALL, label: `All ${label.toLowerCase()}` }, ...options].map((option) => (
              <RadixSelect.Item key={option.value} value={option.value} className={styles.item}>
                <RadixSelect.ItemText>{option.label}</RadixSelect.ItemText>
                <RadixSelect.ItemIndicator>
                  <Icon name="check" size="sm" />
                </RadixSelect.ItemIndicator>
              </RadixSelect.Item>
            ))}
          </RadixSelect.Viewport>
        </RadixSelect.Content>
      </RadixSelect.Portal>
    </RadixSelect.Root>
  );
}
