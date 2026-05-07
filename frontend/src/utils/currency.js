/**
 * Currency formatting utilities for UGX (Ugandan Shillings)
 */

/**
 * Format a number as UGX currency
 * @param {number|string} amount - The amount to format
 * @param {boolean} includeSymbol - Whether to include UGX symbol (default: true)
 * @returns {string} Formatted UGX amount
 */
export const formatUGX = (amount, includeSymbol = true) => {
  const numAmount = parseFloat(amount) || 0;
  const formatted = numAmount.toLocaleString('en-UG', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    useGrouping: true
  });
  
  return includeSymbol ? `UGX ${formatted}` : formatted;
};

/**
 * Format a number as UGX currency with decimal places
 * @param {number|string} amount - The amount to format
 * @param {boolean} includeSymbol - Whether to include UGX symbol (default: true)
 * @returns {string} Formatted UGX amount with 2 decimal places
 */
export const formatUGXWithDecimals = (amount, includeSymbol = true) => {
  const numAmount = parseFloat(amount) || 0;
  const formatted = numAmount.toLocaleString('en-UG', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    useGrouping: true
  });
  
  return includeSymbol ? `UGX ${formatted}` : formatted;
};

/**
 * Parse a formatted UGX amount back to number
 * @param {string} formattedAmount - The formatted amount (e.g., "UGX 500,000")
 * @returns {number} The numeric amount
 */
export const parseUGX = (formattedAmount) => {
  if (!formattedAmount) return 0;
  const cleanAmount = formattedAmount.toString().replace(/[^0-9.-]/g, '');
  return parseFloat(cleanAmount) || 0;
};

/**
 * Default export for convenience
 */
export default formatUGX;
