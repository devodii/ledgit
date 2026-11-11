class ConnectorError(Exception):
    pass


class DomainNotAllowed(ConnectorError):
    pass


class RobotsDisallowed(ConnectorError):
    pass


class HumanActionRequired(ConnectorError):
    def __init__(self, kind: str, description: str, url: str = "", resume_hint: str = "") -> None:
        super().__init__(description)
        self.kind = kind
        self.description = description
        self.url = url
        self.resume_hint = resume_hint
