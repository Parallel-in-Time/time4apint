from dynamic_site.stage.stages import DocsStage, SettingsStage, PlotsStage

from typing import Any


class StagesMessage:

    def __init__(self, docs: list[DocsStage], settings: list[SettingsStage],
                 plots: list[PlotsStage]) -> None:
        self.docs = docs
        self.settings = settings
        self.plots = plots

    def get_stages(
            self
    ) -> tuple[list[DocsStage], list[SettingsStage], list[PlotsStage]]:
        return (self.docs, self.settings, self.plots)


class App:

    def __init__(self) -> None:
        self.docs: list[DocsStage] = []
        self.settings: list[SettingsStage] = []
        self.plots: list[PlotsStage] = []

    def compute(self, response_data: dict[str, Any]) -> StagesMessage:
        raise NotImplementedError('compute in App not implemented')

    def run(self):
        pass
