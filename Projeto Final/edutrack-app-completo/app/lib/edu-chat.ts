export type ChatMessage = { role: 'user' | 'assistant'; text: string };
export type ResponseBlock = { kind: 'text' | 'code'; text: string; language?: string };
export function responseBlocks(text: string): ResponseBlock[] {
  const blocks: ResponseBlock[] = [];
  const pattern = /```([^\n`]*)\n([\s\S]*?)(?:```|$)/g;
  let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index! > cursor) blocks.push({ kind: 'text', text: text.slice(cursor, match.index) });
    blocks.push({ kind: 'code', text: match[2].replace(/\n$/, ''), language: match[1].trim().slice(0, 30) });
    cursor = match.index! + match[0].length;
  }
  if (cursor < text.length) blocks.push({ kind: 'text', text: text.slice(cursor) });
  return blocks;
}
/** Nine messages keeps four complete exchanges plus the latest question. */
export function chatContext(messages: ChatMessage[]): ChatMessage[] { return messages.slice(-9).map(message => ({ ...message, text: message.text.slice(0, 2000) })); }
export function conversationText(messages: ChatMessage[]): string {
  return ['EDUTRACK | CONVERSA DE ESTUDOS', 'Confira as respostas com seus materiais.', '', ...messages.map(m => `${m.role === 'user' ? 'Você' : 'Edu IA'}\n${m.text}\n`)].join('\n');
}
