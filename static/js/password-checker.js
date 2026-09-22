function assessPassword(password) {
  if (!password) {
    return { entropy: 0, percent: 0, color: '#334155', advice: 'Enter a passphrase' };
  }

  let poolSize = 0;
  if (/[a-z]/.test(password)) poolSize += 26;
  if (/[A-Z]/.test(password)) poolSize += 26;
  if (/[0-9]/.test(password)) poolSize += 10;
  if (/[^a-zA-Z0-9]/.test(password)) poolSize += 33;

  if (poolSize === 0) poolSize = 1;

  const entropy = Math.round(password.length * Math.log2(poolSize));
  const percent = Math.min(100, Math.round((entropy / 80) * 100));

  let color = '#f43f5e';
  let advice = 'Weak - vulnerable to fast cracking';

  if (entropy >= 75) {
    color = '#10b981';
    advice = 'Very Strong - computationally infeasible to brute force';
  } else if (entropy >= 50) {
    color = '#38bdf8';
    advice = 'Strong - suitable for sensitive assets';
  } else if (entropy >= 35) {
    color = '#facc15';
    advice = 'Moderate - add special symbols or numbers';
  }

  return { entropy, percent, color, advice };
}