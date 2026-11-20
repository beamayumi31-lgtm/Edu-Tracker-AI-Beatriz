/** Retorna somente os dígitos para comparar CPFs com ou sem máscara. */
export function normalizeCpf(value: string): string {
  return value.replace(/\D/g, '');
}

/** Valida formato e dígitos verificadores; não consulta emissão ou titularidade. */
export function isValidCpf(value: string): boolean {
  if (!/^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$/.test(value.trim())) return false;

  const cpf = normalizeCpf(value);
  if (/^(\d)\1{10}$/.test(cpf)) return false;

  const calculateDigit = (length: number) => {
    const sum = cpf.slice(0, length).split('').reduce(
      (total, digit, index) => total + Number(digit) * (length + 1 - index), 0,
    );
    const remainder = (sum * 10) % 11;
    return remainder === 10 ? 0 : remainder;
  };

  return calculateDigit(9) === Number(cpf[9]) && calculateDigit(10) === Number(cpf[10]);
}

/** Mensagem de correção para o campo de cadastro. */
export function getCpfError(value: string): string | null {
  if (!value.trim()) return 'Informe seu CPF.';
  if (normalizeCpf(value).length !== 11) return 'O CPF deve conter 11 dígitos.';
  if (!isValidCpf(value)) return 'CPF inválido. Confira os números digitados.';
  return null;
}
