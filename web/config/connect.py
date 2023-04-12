import web.stages as stages
import web.config.data as data


def initial_components(
) -> tuple[list[stages.DocsStage], list[stages.SettingsStage],
           list[stages.PlotsStage]]:
    return ([data.stage_1_docs], [data.stage_1_block_problem],
            [data.stage_1_plots])


def compute(
    json_data
) -> tuple[list[stages.DocsStage], list[stages.SettingsStage],
           list[stages.PlotsStage]]:
    # TODO: Create a test plot here and return it
    return ([data.stage_1_docs], [data.stage_1_block_problem],
            [data.stage_1_plots])
