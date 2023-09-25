import pandas as pd
import json
import matplotlib.pyplot as plt

FILE_FORMAT = 'png'


def agg_attempt_collision_near_miss(data):
    d = {}
    d['attempts'] = data['num_collisions'].count()
    d['preventative-meausere'] = (data['num_preventative_maneuvers'] > 0).sum()
    d['collisions'] = data['num_collisions'].sum()
    d['>0-near-miss-occured'] = data['near_miss_occurance'].sum()
    return pd.Series(d)


def create_bar_chart(df, groupby, title, width, height, output_path):
    df_agg = df.groupby([groupby]).apply(agg_attempt_collision_near_miss)
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(width, height))
    # Extracting data for plotting
    categories = df_agg.index
    attributes = ['attempts', 'preventative-meausere', 'collisions', '>0-near-miss-occured']
    data = df_agg[attributes].values

    # Set the bar width
    bar_width = 0.2

    # Create positions for bars
    x = range(len(categories))
    x_positions = []
    for i in range(len(attributes)):
        x_positions.append([j + i * bar_width for j in x])

    # Create the bars
    for i in range(len(attributes)):
        plt.bar(x_positions[i], data[:, i], width=bar_width, label=attributes[i])

    # Set x-axis labels
    plt.xticks([i + (len(attributes) - 1) / 2 * bar_width for i in x], categories)

    # Set the title and legend
    plt.title(title)
    plt.legend()

    # Show the plot
    plt.tight_layout()
    # plt.show()

    # Save the plot
    plt.savefig(f'{output_path}/{title}.{FILE_FORMAT}')


def main():
    input_path = 'fse/data-sim/Town05_2240'
    json_data_actor = json.load(open(f'{input_path}/data_actor.json', 'rb'))
    df_actor = pd.json_normalize(json_data_actor, record_path=['actors'])

    json_data_relationship = json.load(open(f'{input_path}/data_relationship.json', 'rb'))
    df_relationships = pd.json_normalize(json_data_relationship, record_path=['relationships'])
    output_path = 'fse/figures'

    plot_types = [
        (df_actor[df_actor['ego']],                                  'maneuver.id',               'ego____specific Ego attempts per maneuver'                           ),
        (df_actor[df_actor['ego']],                                  'maneuver.type',             'ego________type Ego attempts per maneuver type'                      ),
        (df_actor[df_actor['ego']],                                  'maneuver.start_lane_id',    'ego_______start Ego attempts per start lane'                         ),
        (df_actor[df_actor['ego']],                                  'maneuver.end_lane_id',      'ego_________end Ego attempts per end lane'                           ),
        (df_actor[~df_actor['ego']],                                 'maneuver.id',               'nonego_specific Ego attempts per maneuver'                           ),
        (df_actor[~df_actor['ego']],                                 'maneuver.type',             'nonego_____type Ego attempts per maneuver type'                      ),
        (df_actor[~df_actor['ego']],                                 'maneuver.start_lane_id',    'nonego____start Ego attempts per start lane'                         ),
        (df_actor[~df_actor['ego']],                                 'maneuver.end_lane_id',      'nonego______end Ego attempts per end lane'                           ),
        (df_relationships[df_relationships['time'] == 'initial'],    'relationship',              'rel________init Relationship attempts per relationship (initial)'    ),
        (df_relationships[df_relationships['time'] == 'final'],      'relationship',              'rel_______final Relationship attempts per relationship (final)'      ),
    ]

    for df, groupby, title in plot_types:
        create_bar_chart(df, groupby, title, 8, 4, output_path)

if __name__ == "__main__":
    main()
