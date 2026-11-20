import assert from 'node:assert/strict';
import { test } from 'node:test';
import { canNavigateLocally, isLocalStudyPage } from '../app/lib/study-navigation.ts';

const current = 'https://edutrack.example/dashboard';

test('telas acadêmicas e detalhes usam a navegação local', () => {
  for (const path of ['/cursos', '/cursos/course-1', '/disciplinas/d-1', '/tarefas', '/cronometro', '/edu-ia', '/relatorios', '/ofensiva']) {
    assert.equal(isLocalStudyPage(path), true);
    assert.equal(canNavigateLocally(current, path), true);
  }
});

test('preserva os limites de login, administração e API', () => {
  for (const path of ['/', '/login', '/cadastro', '/gerenciamento', '/api/edu-ia', '/cursos/a/privado']) {
    assert.equal(canNavigateLocally(current, path), false);
    assert.equal(canNavigateLocally('https://edutrack.example' + path, '/dashboard'), false);
  }
});

test('URLs externas, esquemas inseguros e hashes não usam a navegação rápida', () => {
  for (const path of ['https://outro.example/cursos', '//outro.example/cursos', 'javascript:alert(1)', '/cursos#detalhes']) {
    assert.equal(canNavigateLocally(current, path), false);
  }
  assert.equal(canNavigateLocally('URL inválida', '/cursos'), false);
});
