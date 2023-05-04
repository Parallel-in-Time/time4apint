from typing import Any

import web_apps.data as data

from dynamic_site.app import App, StagesMessage


class Accuracy(App):

    def __init__(self) -> None:
        super().__init__()
        self.initialized = False

    def compute(self, response_data: dict[str, Any]) -> StagesMessage:
        if not self.initialized:
            self.initialized = True
            return StagesMessage([data.d1_docs, data.d2_docs],
                                 [data.s1_settings, data.s2_settings],
                                 [data.p1_plots, data.p2_plots])
        docs_d1 = data.d1_docs
        docs_d2 = data.d2_docs

        settings_s1 = data.s1_settings.copy_from_response(response_data)
        settings_s1.activated = True
        settings_s2 = data.s2_settings

        plot_p1 = data.p1_plots.copy_from_response(response_data)
        plot_p1.plot = data.dummy_fig_1()

        if not 'P2' in response_data['plots']:  # If plot doesn't exist yet
            docs_d1 = data.d1_docs.copy()
            docs_d1.activated = True

            plot_p2 = data.p2_plots
        else:  # Otherwise fill it
            plot_p2 = data.p2_plots.copy_from_response(response_data)
            plot_p2.plot = data.dummy_fig_2()

        return StagesMessage([docs_d1, docs_d2], [settings_s1, settings_s2],
                             [plot_p1, plot_p2])
