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
    import plotly.graph_objects as go

    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]]))
    plot_data = fig.to_json()
    plot_p1 = data.stage_1_plots
    plot_p1.plot = plot_data
    return ([data.stage_1_docs], [data.stage_1_block_problem],
            [data.stage_1_plots])
