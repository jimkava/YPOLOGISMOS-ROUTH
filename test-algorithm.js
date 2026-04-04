// Test του Routh-Hurwitz αλγορίθμου
const { calculateRouth } = require('./src/utils/routhCalculator.ts');

console.log('='.repeat(60));
console.log('  ΔΟΚΙΜΗ ΑΛΓΟΡΙΘΜΟΥ ROUTH-HURWITZ');
console.log('='.repeat(60));

// Test ΧΕ 3ου βαθμού
console.log('\n📊 Test 1: ΧΕ 3ου Βαθμού');
console.log('Συντελεστές: a3=1, a2=2, a1=3, K=5');

const result3 = calculateRouth(3, {
  a3: 1,
  a2: 2,
  a1: 3,
  K: 5
});

console.log('\nΧαρακτηριστική Εξίσωση:', result3.characteristicEquation);
console.log('Σταθερότητα:', result3.isStable ? '✓ ΕΥΣΤΑΘΕΣ' : '✗ ΑΣΤΑΘΕΣ');
console.log('Μήνυμα:', result3.message);
console.log('\nΠίνακας Routh:');
result3.routhTable.forEach((row, i) => {
  console.log(`  Γραμμή ${i}:`, row.join('\t'));
});

// Test ΧΕ 2ου βαθμού
console.log('\n\n📊 Test 2: ΧΕ 2ου Βαθμού');
console.log('Συντελεστές: a2=1, a1=2, K=3');

const result2 = calculateRouth(2, {
  a2: 1,
  a1: 2,
  K: 3
});

console.log('\nΧαρακτηριστική Εξίσωση:', result2.characteristicEquation);
console.log('Σταθερότητα:', result2.isStable ? '✓ ΕΥΣΤΑΘΕΣ' : '✗ ΑΣΤΑΘΕΣ');
console.log('Μήνυμα:', result2.message);

// Test ΧΕ 4ου βαθμού
console.log('\n\n📊 Test 3: ΧΕ 4ου Βαθμού');
console.log('Συντελεστές: a4=1, a3=3, a2=3, a1=2, K=1');

const result4 = calculateRouth(4, {
  a4: 1,
  a3: 3,
  a2: 3,
  a1: 2,
  K: 1
});

console.log('\nΧαρακτηριστική Εξίσωση:', result4.characteristicEquation);
console.log('Σταθερότητα:', result4.isStable ? '✓ ΕΥΣΤΑΘΕΣ' : '✗ ΑΣΤΑΘΕΣ');
console.log('Μήνυμα:', result4.message);
if (result4.kCritical) {
  console.log('Κκρ:', result4.kCritical.toFixed(2));
  console.log('ωκρ:', result4.omegaCritical?.toFixed(2), 'rad/s');
}

console.log('\n' + '='.repeat(60));
console.log('✓ Όλα τα tests ολοκληρώθηκαν επιτυχώς!');
console.log('='.repeat(60));
