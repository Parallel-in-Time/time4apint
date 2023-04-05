import web.stages as stages
import web.config.data as data


def initial_components(
) -> tuple[list[stages.DocsStage], list[stages.SettingsStage], list[int]]:
    return ([data.stage_1_docs], [data.stage_1_block_problem], [])


def compute(
    json_data
) -> tuple[list[stages.DocsStage], list[stages.SettingsStage], list[int]]:

    return ([data.stage_1_docs], [data.stage_1_block_problem], [])
