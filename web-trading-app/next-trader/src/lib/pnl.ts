export function calcOpenPnl({
  qty,
  avgPrice,
  last
}: {
  qty: number;
  avgPrice: number;
  last: number;
}) {
  return (last - avgPrice) * qty;
}

export function calcPnlPct({
  pnl,
  avgPrice,
  qty
}: {
  pnl: number;
  avgPrice: number;
  qty: number;
}) {
  const basis = avgPrice * qty;
  return basis === 0 ? 0 : (pnl / basis) * 100;
}

