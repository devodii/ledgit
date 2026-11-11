import { GITHUB_REPO } from '@/api/client';
import { ExternalLink } from '@/components/ui/ExternalLink';
import { STATUS_COPY, StatusBadge, type VerdictStatus } from '@/components/domain/StatusBadge';
import styles from './pages.module.scss';

export function MethodologyPage() {
  return (
    <div className={`${styles.page} ${styles.prose}`}>
      <h1>Methodology</h1>
      <p>
        Ledgit takes specific claims made on stage at Meridian 2025, shows the speaker saying them,
        and reports what public data on the Stellar network says about each one today. We report
        what we found. We do not judge what a team did or intended.
      </p>

      <h2>How claims are selected</h2>
      <ol>
        <li>
          We list the official Meridian 2025 recordings and keep those that match the event title
          and dates.
        </li>
        <li>
          We read each talk's captions with timestamps. Every caption in this event is
          auto-generated, so quotes can contain recognition errors.
        </li>
        <li>
          A language model proposes claims. A claim is a specific statement about something that
          will launch, has launched, or is needed on Stellar, naming a product, asset, corridor,
          feature or date, and checkable against public data.
        </li>
        <li>
          A second, independent pass reviews each claim against the transcript and rejects weak,
          vague or unsupported ones.
        </li>
        <li>We keep the strongest claims per talk and remove duplicates.</li>
      </ol>

      <h2>How quotes are verified</h2>
      <p>
        A quote is only accepted if it is an exact substring of the stored transcript after
        collapsing whitespace. This is enforced in code. If it does not match, the claim is dropped.
        The organisation named must also appear in the transcript, the video title or the video
        description.
      </p>

      <h2>How verdicts are computed</h2>
      <p>
        Verdicts are computed by code from the latest check of every evidence item. No person types
        a status.
      </p>
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>What it means</th>
          </tr>
        </thead>
        <tbody>
          {(Object.keys(STATUS_COPY) as VerdictStatus[]).map((status) => (
            <tr key={status}>
              <td>
                <StatusBadge status={status} />
              </td>
              <td>{MEANING[status]}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <table>
        <thead>
          <tr>
            <th>Evidence</th>
            <th>Found live when</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Asset issuer</td>
            <td>
              The asset exists on mainnet with a non-zero supply and at least the minimum number of
              holders.
            </td>
          </tr>
          <tr>
            <td>Soroban contract</td>
            <td>
              The contract is deployed on mainnet and has invocations inside the activity window.
            </td>
          </tr>
          <tr>
            <td>Anchor</td>
            <td>Its stellar.toml is reachable and at least one declared SEP endpoint responds.</td>
          </tr>
          <tr>
            <td>Protocol upgrade</td>
            <td>The named protocol version is active on mainnet.</td>
          </tr>
        </tbody>
      </table>

      <h2>Where the data comes from</h2>
      <ul>
        <li>
          Primary: YouTube captions, Horizon and Soroban RPC, each organisation's own stellar.toml
          and SEP endpoints, and public Stellar Community Fund pages.
        </li>
        <li>
          Secondary, used to find websites, regions and addresses: the LumenLoop directory and
          StellarLight. Every fact from them is labelled with its source on the claim page.
        </li>
      </ul>

      <h2>Known limits</h2>
      <ul>
        <li>
          Auto-generated captions contain mistakes. We only quote exact caption text, so a mistake
          in the captions appears in the quote.
        </li>
        <li>
          Soroban RPC keeps about seven days of history, so contract activity is checked over that
          window.
        </li>
        <li>
          Linking an organisation to addresses depends on public sources. A missing link means we
          found none, not that none exists.
        </li>
        <li>
          Organisation matching uses exact normalised names, so a different spelling may not match.
        </li>
      </ul>

      <h2>How to correct an entry</h2>
      <p>
        Every claim page has a "Suggest a correction" link that opens a prefilled GitHub issue. To
        fix or add evidence yourself, open a pull request, see the contributor guide in the{' '}
        <ExternalLink href={`https://github.com/${GITHUB_REPO}`}>repository</ExternalLink>.
      </p>
    </div>
  );
}

const MEANING: Record<VerdictStatus, string> = {
  live: 'At least one evidence item was found live on mainnet by our latest check.',
  testnet_only: 'Evidence was found on testnet but not on mainnet.',
  no_trace_found:
    'We could not find any on-chain trace for the evidence we linked, or we linked none.',
  pending:
    'The talk is too recent, or evidence is present but activity could not be confirmed yet.',
  open_ask: 'The speaker asked for something to be built and named no builder.',
};
