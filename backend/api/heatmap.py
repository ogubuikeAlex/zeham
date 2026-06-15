from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from sqlalchemy import select

from db.database import AsyncSessionLocal
from db.models import Alert, WatchedContract

router = APIRouter()

_RANGES = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}
_SEVERITY_RANK = {'NONE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}


def _worst(a: str, b: str) -> str:
    return a if _SEVERITY_RANK.get(a, 0) >= _SEVERITY_RANK.get(b, 0) else b


@router.get('/heatmap')
async def get_heatmap(range: str = '24h'):
    now = datetime.now(timezone.utc)
    cutoff = now - _RANGES.get(range, _RANGES['24h'])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Alert.contract_address, Alert.severity, Alert.fired_at)
            .where(Alert.fired_at >= cutoff)
        )
        rows = result.all()
        labels = dict(
            (await session.execute(select(WatchedContract.address, WatchedContract.label))).all()
        )

    # (contract, hour) -> {count, worst_severity}
    cells: dict[tuple[str, int], dict] = {}
    # contract -> aggregate stats for top_offenders
    offenders: dict[str, dict] = defaultdict(
        lambda: {'total_alerts': 0, 'critical_count': 0, 'high_count': 0, 'hours': defaultdict(int)}
    )

    for address, severity, fired_at in rows:
        hour = fired_at.hour if fired_at else 0
        key = (address, hour)
        cell = cells.get(key)
        if cell is None:
            cells[key] = {'alert_count': 1, 'worst_severity': severity}
        else:
            cell['alert_count'] += 1
            cell['worst_severity'] = _worst(cell['worst_severity'], severity)

        o = offenders[address]
        o['total_alerts'] += 1
        if severity == 'CRITICAL':
            o['critical_count'] += 1
        elif severity == 'HIGH':
            o['high_count'] += 1
        o['hours'][hour] += 1

    cell_list = [
        {
            'contract_address': address,
            'contract_label': labels.get(address),
            'hour': hour,
            'alert_count': c['alert_count'],
            'worst_severity': c['worst_severity'],
        }
        for (address, hour), c in cells.items()
    ]

    top_offenders = sorted(
        (
            {
                'contract_address': address,
                'contract_label': labels.get(address),
                'total_alerts': o['total_alerts'],
                'critical_count': o['critical_count'],
                'high_count': o['high_count'],
                'peak_hour': max(o['hours'].items(), key=lambda kv: kv[1])[0] if o['hours'] else 0,
            }
            for address, o in offenders.items()
        ),
        key=lambda x: x['total_alerts'],
        reverse=True,
    )[:10]

    return {
        'cells': cell_list,
        'top_offenders': top_offenders,
        'generated_at': now.isoformat(),
    }
