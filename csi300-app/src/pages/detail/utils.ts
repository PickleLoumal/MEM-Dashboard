export function formatNumber(value: number | string | undefined | null, decimals = 0): string {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) {
    return '-';
  }
  
  return num.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

export function formatDate(dateString: string | undefined): string {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  } catch {
    return dateString;
  }
}

export function getImSectorDisplay(company: any): string {
    if (!company) return '';
    return company.im_sector || company.industry || company.im_code || 'Unknown Industry Matrix Sector';
}

