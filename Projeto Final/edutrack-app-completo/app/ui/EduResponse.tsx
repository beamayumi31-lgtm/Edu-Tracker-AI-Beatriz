'use client';
import { Fragment } from 'react';
import { responseBlocks } from '../lib/edu-chat';
function inline(text: string) {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => part.startsWith('**') && part.endsWith('**') ? <strong key={i}>{part.slice(2,-2)}</strong> : part.startsWith('`') && part.endsWith('`') ? <code key={i}>{part.slice(1,-1)}</code> : <Fragment key={i}>{part}</Fragment>);
}
export default function EduResponse({ text }: { text: string }) {
  return <div className="edu-response">{responseBlocks(text).map((block,i) => block.kind === 'code' ? <div className="edu-code" key={i}><span>{block.language || 'Código'}</span><pre><code>{block.text}</code></pre></div> : <div key={i}>{block.text.split('\n').map((line,j) => /^#{1,3}\s/.test(line) ? <h3 key={j}>{inline(line.replace(/^#{1,3}\s/,''))}</h3> : <p key={j}>{inline(line) || '\u00a0'}</p>)}</div>)}</div>;
}
