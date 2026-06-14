import logging
from dataclasses import dataclass

from constants import EventType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EventSpec:
    name: str
    topic0: str         
    from_topic: int | None   
    to_topic: int | None     


EVENT_SPECS: dict[str, EventSpec] = {
    EventType.TRANSFER.value: EventSpec(
        EventType.TRANSFER.value,
        '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', 1, 2),
    EventType.APPROVAL.value: EventSpec(
        EventType.APPROVAL.value,
        '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925', 1, 2),
    EventType.SWAP.value: EventSpec(
        EventType.SWAP.value,
        '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822', 1, 2),
    EventType.MINT.value: EventSpec(
        EventType.MINT.value,
        '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f', 1, None),
    EventType.BURN.value: EventSpec(
        EventType.BURN.value,
        '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496', 1, 2),
    EventType.LIQUIDATION.value: EventSpec(
        EventType.LIQUIDATION.value,
        '0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286', 3, 1),
}

_TOPIC0_TO_SPEC = {spec.topic0: spec for spec in EVENT_SPECS.values()}

EVENT_SIGNATURES = {name: spec.topic0 for name, spec in EVENT_SPECS.items()}


def _hexstr(value) -> str:
    if isinstance(value, (bytes, bytearray)):
        value = '0x' + value.hex()
    value = str(value)
    if not value.startswith('0x'):
        value = '0x' + value
    return value.lower()


def _topic_to_address(topic) -> str | None:
    if topic is None:
        return None
    h = _hexstr(topic)[2:]
    return '0x' + h[-40:].lower() if h else None


def resolve_event_type(log) -> str:
    topics = log.get('topics') if hasattr(log, 'get') else log['topics']
    if not topics:
        return EventType.UNKNOWN.value
    spec = _TOPIC0_TO_SPEC.get(_hexstr(topics[0]))
    return spec.name if spec else EventType.UNKNOWN.value


def decode_log(log) -> dict:
    topics = log.get('topics') if hasattr(log, 'get') else log['topics']
    if not topics:
        return {'event_type': EventType.UNKNOWN.value, 'from_address': None, 'to_address': None}

    spec = _TOPIC0_TO_SPEC.get(_hexstr(topics[0]))
    if spec is None:
        from_t = 1 if len(topics) > 1 else None
        to_t = 2 if len(topics) > 2 else None
        event_type = EventType.UNKNOWN.value
    else:
        from_t, to_t, event_type = spec.from_topic, spec.to_topic, spec.name

    def at(idx):
        return _topic_to_address(topics[idx]) if idx is not None and len(topics) > idx else None

    return {'event_type': event_type, 'from_address': at(from_t), 'to_address': at(to_t)}
