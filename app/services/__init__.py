from app.panels import ServiceModule

from .infra import InfraService
from .lck_pics import LckPicsService
from .reflexion_rondo import ReflexionRondoService

SERVICES: list[ServiceModule] = [
    InfraService(),
    ReflexionRondoService(),
    LckPicsService(),
]
