export interface RouthResult {
  isStable: boolean;
  routhTable: (number | string)[][];
  message: string;
  kCritical?: number;
  omegaCritical?: number;
  characteristicEquation: string;
}

export interface Coefficients {
  [key: string]: number;
}

/**
 * Υπολογίζει το κριτήριο σταθερότητας Routh-Hurwitz
 * @param degree Βαθμός της χαρακτηριστικής εξίσωσης (1-6)
 * @param coefficients Οι συντελεστές της εξίσωσης
 * @returns Αποτελέσματα ανάλυσης σταθερότητας
 */
export function calculateRouth(
  degree: number,
  coefficients: Coefficients
): RouthResult {
  switch (degree) {
    case 1:
      return calculateRouthDegree1(coefficients);
    case 2:
      return calculateRouthDegree2(coefficients);
    case 3:
      return calculateRouthDegree3(coefficients);
    case 4:
      return calculateRouthDegree4(coefficients);
    case 5:
      return calculateRouthDegree5(coefficients);
    case 6:
      return calculateRouthDegree6(coefficients);
    default:
      throw new Error('Μη υποστηριζόμενος βαθμός εξίσωσης');
  }
}

function calculateRouthDegree1(coeff: Coefficients): RouthResult {
  const { a1, K } = coeff;
  const characteristicEquation = `${a1}s + ${K} = 0`;

  const isStable = (a1 > 0 && K > 0) || (a1 < 0 && K < 0);

  return {
    isStable,
    routhTable: [
      [a1, K]
    ],
    message: isStable ? 'Το Σύστημα είναι ΕΥΣΤΑΘΕΣ' : 'Το Σύστημα είναι ΑΣΤΑΘΕΣ',
    characteristicEquation
  };
}

function calculateRouthDegree2(coeff: Coefficients): RouthResult {
  const { a2, a1, K } = coeff;
  const characteristicEquation = `${a2}s² + ${a1}s + ${K} = 0`;

  const isStable = (a2 > 0 && a1 > 0 && K > 0) || (a2 < 0 && a1 < 0 && K < 0);

  return {
    isStable,
    routhTable: [
      [a2, K],
      [a1, 0]
    ],
    message: isStable ? 'Το Σύστημα είναι ΕΥΣΤΑΘΕΣ' : 'Το Σύστημα είναι ΑΣΤΑΘΕΣ',
    characteristicEquation
  };
}

function calculateRouthDegree3(coeff: Coefficients): RouthResult {
  const { a3, a2, a1, K } = coeff;
  const characteristicEquation = `${a3}s³ + ${a2}s² + ${a1}s + K = 0`;

  const b1 = a1 - (a3 * K) / a2;

  const routhTable = [
    [a3, a1, 0],
    [a2, K, 0],
    [b1, 0, 0],
    ['K', 0, 0]
  ];

  const kCritical = (a1 * a2) / a3;
  const omegaCritical = kCritical > 0 ? Math.sqrt(kCritical / a2) : 0;

  const isStable = a3 > 0 && a2 > 0 && kCritical > 0;

  const message = isStable
    ? `Το Σύστημα είναι ΕΥΣΤΑΘΕΣ για K < ${kCritical.toFixed(2)}\nΚκρ = ${kCritical.toFixed(2)}, ωκρ = ${omegaCritical.toFixed(2)}`
    : 'Το Σύστημα είναι ΑΣΤΑΘΕΣ';

  return {
    isStable,
    routhTable,
    message,
    kCritical,
    omegaCritical,
    characteristicEquation
  };
}

function calculateRouthDegree4(coeff: Coefficients): RouthResult {
  const { a4, a3, a2, a1, K } = coeff;
  const characteristicEquation = `${a4}s⁴ + ${a3}s³ + ${a2}s² + ${a1}s + K = 0`;

  const b1 = a2 - (a4 * a1) / a3;
  const c1 = a1 - (a3 * K) / b1;

  const routhTable = [
    [a4, a2, K, 0],
    [a3, a1, 0, 0],
    [b1, K, 0, 0],
    [c1, 0, 0, 0],
    ['K', 0, 0, 0]
  ];

  const kCritical = (a1 * b1) / a3;
  const omegaCritical = kCritical > 0 && b1 > 0 ? Math.sqrt(kCritical / b1) : 0;

  const isStable = a4 > 0 && a3 > 0 && b1 > 0 && kCritical > 0;

  const message = isStable
    ? `Το Σύστημα είναι ΕΥΣΤΑΘΕΣ για K < ${kCritical.toFixed(2)}\nΚκρ = ${kCritical.toFixed(2)}, ωκρ = ${omegaCritical.toFixed(2)}`
    : 'Το Σύστημα είναι ΑΣΤΑΘΕΣ';

  return {
    isStable,
    routhTable,
    message,
    kCritical,
    omegaCritical,
    characteristicEquation
  };
}

function calculateRouthDegree5(coeff: Coefficients): RouthResult {
  const { a5, a4, a3, a2, a1, K } = coeff;
  const characteristicEquation = `${a5}s⁵ + ${a4}s⁴ + ${a3}s³ + ${a2}s² + ${a1}s + K = 0`;

  const b1 = a3 - (a5 * a2) / a4;
  const b2 = a1 - (a3 * K) / b1;
  const x = (b2 * a1 * a4 - a5 * b2) / (Math.pow(a5, 2) - a1 * a4 * a5 + a4 * b1);
  const c1 = b2 + a5 * x;
  const c2 = a5 / a4 + b1 / c1;

  const routhTable = [
    [a5, a3, a1, 0],
    [a4, a2, 'K', 0],
    [b1, `${a1}-(${a5}/${a4})K`, 0, 0],
    [`${b2}+${a5}K`, 'K', 0, 0],
    [`${a1}-(${c2})K`, 'K', 0, 0],
    ['K', 0, 0, 0]
  ];

  const kCritical = a1 / c2;
  const omegaCritical = kCritical > 0 && c1 > 0 ? Math.sqrt(kCritical / c1) : 0;

  const isStable = a5 > 0 && a4 > 0 && b1 > 0 && c1 > 0 && kCritical > 0;

  const message = isStable
    ? `Το Σύστημα είναι ΕΥΣΤΑΘΕΣ για K < ${kCritical.toFixed(2)}\nΚκρ = ${kCritical.toFixed(2)}, ωκρ = ${omegaCritical.toFixed(2)}`
    : 'Το Σύστημα είναι ΑΣΤΑΘΕΣ';

  return {
    isStable,
    routhTable,
    message,
    kCritical,
    omegaCritical,
    characteristicEquation
  };
}

function calculateRouthDegree6(coeff: Coefficients): RouthResult {
  const { a6, a5, a4, a3, a2, a1, K } = coeff;
  const characteristicEquation = `${a6}s⁶ + ${a5}s⁵ + ${a4}s⁴ + ${a3}s³ + ${a2}s² + ${a1}s + K = 0`;

  const b1 = a4 - (a6 * a3) / a5;
  const b2 = a2 - (a4 * a1) / a3;
  const c1 = a3 - (a5 * b2) / b1;
  const x1 = b2 - (b1 * a1) / c1;
  const c2 = a5 / a4 + b1 / c1;

  const routhTable = [
    [a6, a4, a2, 'K', 0],
    [a5, a3, a1, 0, 0],
    [b1, b2, 'K', 0, 0],
    [c1, `${a1}-(${a5}/${b1})K`, 0, 0, 0],
    [`${x1}-(${a5}/${c1})K`, 'K', 0, 0, 0],
    [`${a1}-(${c2})K`, 'K', 0, 0, 0],
    ['K', 0, 0, 0, 0]
  ];

  const kCritical = a1 / c2;
  const omegaCritical = kCritical > 0 && c1 > 0 ? Math.sqrt(kCritical / c1) : 0;

  const isStable = a5 > 0 && a4 > 0 && b1 > 0 && c1 > 0 && kCritical > 0;

  const message = isStable
    ? `Το Σύστημα είναι ΕΥΣΤΑΘΕΣ για K < ${kCritical.toFixed(2)}\nΚκρ = ${kCritical.toFixed(2)}, ωκρ = ${omegaCritical.toFixed(2)}`
    : 'Το Σύστημα είναι ΑΣΤΑΘΕΣ';

  return {
    isStable,
    routhTable,
    message,
    kCritical,
    omegaCritical,
    characteristicEquation
  };
}
