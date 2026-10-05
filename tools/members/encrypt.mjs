// Usage: node tools/members/encrypt.mjs "<password>" tools/members/content.html > members.html
import { readFileSync } from 'node:fs';
import { webcrypto as crypto } from 'node:crypto';
const [pw, file] = process.argv.slice(2);
const content = readFileSync(file, 'utf8');
const enc = new TextEncoder();
const salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveKey']);
const key = await crypto.subtle.deriveKey({ name: 'PBKDF2', salt, iterations: 250000, hash: 'SHA-256' }, base, { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, enc.encode(content)));
const b64 = u => Buffer.from(u).toString('base64');
const tpl = readFileSync(new URL('./template.html', import.meta.url), 'utf8');
process.stdout.write(tpl.replace('__SALT__', b64(salt)).replace('__IV__', b64(iv)).replace('__DATA__', b64(ct)));
