import { rmSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// Never leave a previously built draft or deleted article in the deployment.
const root = fileURLToPath(new URL('../', import.meta.url));
rmSync(new URL('../dist/', import.meta.url), { recursive: true, force: true });
const result = spawnSync(process.execPath, ['node_modules/@11ty/eleventy/cmd.cjs', ...process.argv.slice(2)], {
  cwd: root, stdio: 'inherit'
});
process.exit(result.status ?? 1);
