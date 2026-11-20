import assert from 'node:assert/strict';
import { test } from 'node:test';
import { getCpfError, isValidCpf, normalizeCpf } from '../app/lib/cpf.ts';

// Números sintéticos: estes testes não comprovam emissão ou titularidade.
test('aceita os dígitos verificadores de um exemplo com e sem máscara', () => {
  assert.equal(isValidCpf('00000000191'), true);
  assert.equal(isValidCpf('000.000.001-91'), true);
  assert.equal(normalizeCpf('000.000.001-91'), '00000000191');
  assert.equal(getCpfError('000.000.001-91'), null);
});

test('rejeita sequências repetidas, mesmo quando passam pelo cálculo', () => {
  for (let digit = 0; digit <= 9; digit++) {
    assert.equal(isValidCpf(String(digit).repeat(11)), false);
  }
});

test('rejeita alterações em cada dígito verificador', () => {
  assert.equal(isValidCpf('00000000181'), false);
  assert.equal(isValidCpf('00000000190'), false);
});

test('rejeita valores incompletos, longos ou com caracteres inesperados', () => {
  for (const value of ['', '0000000019', '000000001910', 'abc00000000191', '000-000-001.91']) {
    assert.equal(isValidCpf(value), false);
  }
});

test('apresenta mensagens distintas para campo vazio, incompleto e inválido', () => {
  assert.equal(getCpfError(''), 'Informe seu CPF.');
  assert.equal(getCpfError('123'), 'O CPF deve conter 11 dígitos.');
  assert.equal(getCpfError('000.000.000-00'), 'CPF inválido. Confira os números digitados.');
});
