import { Time } from 'lightweight-charts';

export function calculateMA(data: { time: Time; value: number }[], period: number) {
  const maData = [];
  for (let i = period - 1; i < data.length; i++) {
    const sum = data.slice(i - period + 1, i + 1).reduce((acc, d) => acc + d.value, 0);
    maData.push({
      time: data[i].time,
      value: sum / period,
    });
  }
  return maData;
}

export function convertToChartTime(dateStr: string | undefined, isIntraday: boolean): Time {
  if (!dateStr) return 0 as Time;
  if (isIntraday) {
    // Expecting "YYYY-MM-DD HH:MM:SS" or similar
    // Convert to unix timestamp
    return (new Date(dateStr).getTime() / 1000) as Time;
  }
  // For daily, expect "YYYY-MM-DD"
  // Lightweight charts expects string 'YYYY-MM-DD' for daily
  return dateStr.split(' ')[0] as Time;
}

export function formatNumber(value: number | undefined, decimals = 2): string {
  if (value === undefined || value === null || isNaN(value)) return '--';
  return value.toFixed(decimals);
}

export function formatLargeNumber(value: number | undefined): string {
    if (value === undefined || value === null || isNaN(value)) return '--';
    return value.toLocaleString('en-US');
}

