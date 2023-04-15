import web.stage.stages as stages
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
    print(json_data)

    import plotly.graph_objects as go

    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]], ))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    plot_data = fig.to_json()

    plot_p1 = stages.PlotsStage('P1', 'Error', data.p1_params, None, None)
    plot_p1.plot = plot_data

    fig = go.Figure(data=go.Contour(
        z=[[10, 10.625, 12.5, 15.625, 20], [5.625, 6.25, 8.125, 11.25, 15.625],
           [2.5, 3.125, 5., 8.125, 12.5], [0.625, 1.25, 3.125, 6.25, 10.625],
           [0, 0.625, 2.5, 5.625, 10]],
        x=[-9, -6, -5, -3, -1],
        y=[0, 1, 4, 5, 7]))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), autosize=True)
    plot_data = fig.to_json()

    plot_p2 = stages.PlotsStage('P2', 'Test', data.p1_params, None, None)
    plot_p2.plot = plot_data

    return ([data.stage_1_docs], [data.stage_1_block_problem],
            [plot_p1, plot_p2])
