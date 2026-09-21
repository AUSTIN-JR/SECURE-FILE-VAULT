function assessPassword(password) {
  let poolSize = 0;
  if (/[a-z]/.test(password)) poolSize += 26;
  if (/[A-Z]/.test(password)) poolSize += 26;
  if (/[0-9]/.test(password)) poolSize += 10;
  if (/[^a-zA-Z0-9]/.test(password)) poolSize += 32;

  const entropy = password.length > 0 && poolSize > 0
    ? Math.round(password.length * Math.log2(poolSize))
    : 0;

  let advice = "Too weak";
  let color = "#f85149";
  let percent = Math.min((entropy / 80) * 100, 100);

  if (entropy >= 60 && password.length >= 12) {
    advice = "Strong";
    color = "#2ea043";
  } else if (entropy >= 40) {
    advice = "Moderate";
    color = "#d29922";
  }

  return { entropy, percent, color, advice };
}