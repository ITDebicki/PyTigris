import enum
import logging

logger = logging.getLogger(__name__)

class Resolution(enum.Enum):
    R500K = '500k'
    R5M = '5m'
    R20M = '20m'

class SchoolDistrict(enum.Enum):
    UNIFIED = 'unsd'
    ELEMENTARY = 'elsd'
    SECONDARY = 'scsd'

    @classmethod
    def _missing_(cls, name):
        name = name.upper()
        name_lower = name.lower()
        for member in cls:
            if member.name == name or member.value == name_lower:
                return member
        return None

SUMMARY_LEVEL_CODES = {
    'region': '020',
    'division': '030',
    'state': '040',
    'county': '050',
    'tract': '140',
    'block': '150',
    'bg': '150',
    'place': '160',
    'elsd': '950',
    'scsd': '960',
    'unsd': '970'
}