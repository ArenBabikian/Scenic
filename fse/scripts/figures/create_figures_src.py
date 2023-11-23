import os
import pandas as pd
import json
import matplotlib.pyplot as plt

FILE_FORMAT = 'png'


def agg_attempt_collision_near_miss(data):
    d = {}
    d['attempts'] = data['num_collisions'].count()
    d['near miss'] = data['near_miss_occurance'].sum()
    d['collision'] = data['num_collisions'].sum()
    # d['preventative meausere'] = (data['num_preventative_maneuvers'] > 0).sum()
    return pd.Series(d)


def create_bar_chart(df, groupby, title, xlabel, width, height, output_path):
    df_agg = df.groupby([groupby]).apply(agg_attempt_collision_near_miss)

    if groupby == 'maneuver.id':
        allowed = {'road981_lane0': 'tl_south', 'road949_lane0': 'tl_north', 'road974_lane0': 'tl_east', 'road962_lane0': 'tl_west'}
        fig, ax = plt.subplots(figsize=(4, 3))  # Change the figsize parameter here
    else:
        allowed = {'left': 'turnsLeft', 'right': 'turnsRight', 'straight': 'goesStraight'}
        fig, ax = plt.subplots(figsize=(3.33, 3))  # Change the figsize parameter here

    df_agg = df_agg.loc[df_agg.index.isin(allowed)]
    categories = [allowed[x] for x in df_agg.index]
    
    # Extracting data for plotting
    
    attributes = ['attempts', 'near miss', 'collision']
    labels = ['success', 'near-miss', 'collision']
    data = df_agg[attributes].values

    # STATISTICAL SIGNIFICANCE
    from scipy.stats import fisher_exact
    print(">>>Success Rate Statistical Significance<<<")
    print(data)

    thresh=0.05
    for i, dc in enumerate(data):
        print(f'    {categories[i]}(at={dc[0]}, nm={dc[1]}, col={dc[2]})')
    print()

    combos = [(1, 1), (2, 2), (1, 2), (2, 1)] 
    names = ['at', 'nm', 'col']
    for i, dci in enumerate(data):
        at1 = dci[0]
        nm1 = dci[1]
        col1 = dci[2]
        for j, dcj in enumerate(data[i+1:]):
            at2 = dcj[0]
            nm2 = dcj[1]
            col2 = dcj[2]
            print(f'    {categories[i]}-{categories[j+i+1]}')
            for c in combos:
                oddsratio, pvaluerm = fisher_exact([[at1, dci[c[0]]],[at2, dcj[c[1]]]])
                oddsratio, pvaluerm = fisher_exact([[at2, dcj[c[1]]],[at1, dci[c[0]]]])

                print(('~~~~' if pvaluerm>thresh else '    ') + f' {names[c[0]].ljust(4)} * {names[c[1]].ljust(4)} : (pvalue={pvaluerm:.3f}) (oddsrat={oddsratio:.3f})')
    print(">>>End Statistical Significance<<<")
    # END STATISTICAL SIGNIFICANCE

    # NORMALIZE DATA
    for i, d in enumerate(data):
        d2 = d / d.max() * 100
        data[i] = d2

    # Set the bar width
    bar_width = 0.8
    # bar_width = 1

    # Create positions for bars
    x = range(len(categories))
    x_positions = []
    for i in range(len(attributes)):
        x_positions.append([j+bar_width for j in x])
        # x_positions.append([j + i * bar_width for j in x])

    # Create the bars
    for i in range(len(attributes)):
        plt.bar(x_positions[i], data[:, i], width=bar_width, label=labels[i])
        # plt.bar(x_positions[i], data[:, i], width=bar_width, label=attributes[i])

    # Set x-axis labels
    plt.xticks([i + (len(attributes) - 1) / 2 * bar_width for i in x], categories)
    # Add axis titles
    ax.set_ylabel('Percentage of scenarios')

    # Add axis titles
    ax.set_xlabel(xlabel)

    # Show the plot
    plt.tight_layout()

    # Save the plot
    plt.savefig(f'{output_path}/{title}.{FILE_FORMAT}')
    os.makedirs(f'{output_path}/csv', exist_ok=True)
    df_agg.to_csv(f'{output_path}/csv/{title}.csv')

    os.makedirs(f'{output_path}/latex', exist_ok=True)
    with open(f'{output_path}/latex/{title}.tex', 'w') as f:
        f.write(df_agg.to_latex())

    # EXPORT LEGEND
    plt.axis('off')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
                    box.width, box.height * 0.9])

    # Put a legend below current axis
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=4)

    # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(f'{output_path}/legend.{FILE_FORMAT}', dpi=300, bbox_inches=bbox)


def main():
    input_path = 'fse/data-sim'
    output_path = 'fse/figures/src/evaluation'
    os.makedirs(output_path, exist_ok=True)

    map_junction_names = ['Town04_916']
    actor_df_list = []
    relationship_list = []
    coordinatess_list = []
    for map_junction_name in map_junction_names:
        json_data_actor = json.load(open(f'{input_path}/{map_junction_name}/data_actor.json', 'rb'))
        df_act = pd.json_normalize(json_data_actor, record_path=['actors'])
        actor_df_list.append(df_act)

        json_data_relationship = json.load(open(f'{input_path}/{map_junction_name}/data_relationship.json', 'rb'))
        df_rel = pd.json_normalize(json_data_relationship, record_path=['relationships'])
        relationship_list.append(df_rel)

        dc_coord = pd.read_csv(f'{input_path}/{map_junction_name}/path_coords.csv')
        coordinatess_list.append(dc_coord)

    df_actor = pd.concat(actor_df_list)    

    plot_types = [
        (df_actor[df_actor['ego']], 'maneuver.id',   'log-res'      , 'Logical Maneuver'),
        (df_actor[df_actor['ego']], 'maneuver.type', 'fun-res' , 'Functional maneuver')
    ]

    for df, groupby, title, xlabel in plot_types:
        create_bar_chart(df=df, groupby=groupby, title=title, xlabel=xlabel, width=8, height=4, output_path=output_path)

if __name__ == "__main__":
    main()
