import test from 'node:test';
import assert from 'node:assert/strict';
import { responseBlocks, chatContext, conversationText } from '../app/lib/edu-chat.ts';
test('separa código sem interpretar HTML ou links', () => {
  assert.deepEqual(responseBlocks('Exemplo\n```sql\nSELECT 1;\n```\n<script>x</script>'), [{kind:'text',text:'Exemplo\n'}, {kind:'code',text:'SELECT 1;',language:'sql'}, {kind:'text',text:'\n<script>x</script>'}]);
});
test('aceita bloco de código incompleto e resposta vazia', () => {
  assert.deepEqual(responseBlocks('```\na < b'), [{kind:'code',text:'a < b',language:''}]);
  assert.deepEqual(responseBlocks(''), []);
});
test('contexto limita pares completos mantendo a pergunta mais recente', () => {
  const messages = Array.from({length:13},(_,i)=>({role:i%2?'assistant':'user',text:String(i)}));
  const result=chatContext(messages); assert.equal(result.length,9); assert.equal(result[0].role,'user'); assert.equal(result.at(-1).text,'12'); assert.equal(messages.length,13);
});
test('exporta conversa como texto com autoria explícita', () => {
  assert.match(conversationText([{role:'user',text:'Olá'},{role:'assistant',text:'Oi'}]), /Você\nOlá\n\nEdu IA\nOi/);
});
test('limita respostas longas no contexto sem alterar a conversa visível', () => {
  const messages=[{role:'assistant',text:'a'.repeat(5000)},{role:'user',text:'Continue'}];
  assert.equal(chatContext(messages)[0].text.length,2000);assert.equal(messages[0].text.length,5000);
});
