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
    d['preventative meausere'] = (data['num_preventative_maneuvers'] > 0).sum()
    return pd.Series(d)


def create_bar_chart(df, groupby, title, xlabel, width, height, output_path):
    df_agg = df.groupby([groupby]).apply(agg_attempt_collision_near_miss)
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(width, height))
    # Extracting data for plotting
    categories = df_agg.index
    attributes = ['attempts', 'near miss', 'collision', 'preventative meausere']
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

    # Add axis titles
    ax.set_xlabel(xlabel)

    # Show the plot
    plt.tight_layout()
    # plt.show()

    # Save the plot
    plt.savefig(f'{output_path}/{title}.{FILE_FORMAT}')
    os.makedirs(f'{output_path}/csv', exist_ok=True)
    df_agg.to_csv(f'{output_path}/csv/{title}.csv')

    os.makedirs(f'{output_path}/latex', exist_ok=True)
    with open(f'{output_path}/latex/{title}.tex', 'w') as f:
        f.write(df_agg.to_latex())
    plt.close()


def create_coordinates_chart(df, man_id, title, width, height, output_path, fix_scale=False):
    # Filter the DataFrame based on the condition 'man_id'
    filtered_df = df[df['man_id'] == man_id]

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(width, height))
    if fix_scale:
        ax.set_aspect('equal', adjustable='box')

    # Define discrete colors for each unique 'num_actors' value
    unique_num_actors = filtered_df['num_actors'].unique()
    colors = plt.cm.tab10.colors[:len(unique_num_actors)]

    # Create a legend handler map for dot markers
    legend_handles = []
    for num_actor, color in zip(unique_num_actors, colors):
        legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=8, label=f'num_actors={num_actor}'))

    # Create the scatter plot with discrete colors
    for num_actor, color in zip(unique_num_actors, colors):
        subset_df = filtered_df[filtered_df['num_actors'] == num_actor]
        ax.scatter(subset_df['x'], subset_df['y'], label=f'num_actors={num_actor}', color=color, alpha=0.2, s=5)

    # Set the title
    ax.set_title(title)

    # Add the legend with dot markers
    ax.legend(handles=legend_handles)

    if fix_scale and ('80' in man_id or '81' in man_id):
        # Adjust the y-axis limits to cover more area
        ax.set_ylim(bottom=min(filtered_df['y']) - 5, top=max(filtered_df['y']) + 10)  # You can adjust the padding as needed

    # Add axis titles
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    plt.tight_layout()

    # Show the plot
    # plt.show()

    # Save the plot
    plt.savefig(f'{output_path}/{title}.{FILE_FORMAT}')
    plt.close()


# Function to create coordinates chart
def create_coordinates_composite_chart(df, man_id, title, ax, fix_scale=False):
    # Filter the DataFrame based on the condition 'man_id'
    filtered_df = df[df['man_id'] == man_id]

    if fix_scale:
        ax.set_aspect('equal', adjustable='box')

    # Define discrete colors for each unique 'num_actors' value
    unique_num_actors = filtered_df['num_actors'].unique()
    colors = plt.cm.tab10.colors[:len(unique_num_actors)]

    # Create a legend handler map for dot markers
    legend_handles = []
    for num_actor, color in zip(unique_num_actors, colors):
        legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=8, label=f'num_actors={num_actor}'))

    # Create the scatter plot with discrete colors
    for num_actor, color in zip(unique_num_actors, colors):
        subset_df = filtered_df[filtered_df['num_actors'] == num_actor]
        ax.scatter(subset_df['x'], subset_df['y'], label=f'num_actors={num_actor}', color=color, alpha=0.2, s=5)

    # Set the title
    ax.set_title(title)

    # Add the legend with dot markers
    ax.legend(handles=legend_handles)

    if fix_scale and ('80' in man_id or '81' in man_id):
        # Adjust the y-axis limits to cover more area
        ax.set_ylim(bottom=min(filtered_df['y']) - 5, top=max(filtered_df['y']) + 10)  # You can adjust the padding as needed

    # Add axis titles
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    
    plt.tight_layout()


def main():
    input_path = 'fse/data-sim'
    output_path = 'fse/figures'
    os.makedirs(output_path, exist_ok=True)

    map_junction_names = ['Town04_916', 'Town05_2240']
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
    df_relationship = pd.concat(relationship_list)
    df_coordinates = pd.concat(coordinatess_list)
    

    plot_types = [
        (df_actor[df_actor['ego']],                               'maneuver.id',            'ego____specific Ego attempts per maneuver'                        , 'Maneuver id'),
        (df_actor[df_actor['ego']],                               'maneuver.type',          'ego________type Ego attempts per maneuver type'                   , 'Maneuver type'),
        (df_actor[df_actor['ego']],                               'maneuver.start_lane_id', 'ego_______start Ego attempts per start lane'                      , 'Start lane'),
        (df_actor[df_actor['ego']],                               'maneuver.end_lane_id',   'ego_________end Ego attempts per end lane'                        , 'End lane'),
        (df_actor[~df_actor['ego']],                              'maneuver.id',            'nonego_specific Ego attempts per maneuver'                        , 'Maneuver id'),
        (df_actor[~df_actor['ego']],                              'maneuver.type',          'nonego_____type Ego attempts per maneuver type'                   , 'Maneuver type'),
        (df_actor[~df_actor['ego']],                              'maneuver.start_lane_id', 'nonego____start Ego attempts per start lane'                      , 'Start lane'),
        (df_actor[~df_actor['ego']],                              'maneuver.end_lane_id',   'nonego______end Ego attempts per end lane'                        , 'End lane'),
        (df_relationship[df_relationship['time'] == 'initial'], 'relationship',           'rel________init Relationship attempts per relationship (initial)' , 'Initial relationship'),
        (df_relationship[df_relationship['time'] == 'final'],   'relationship',           'rel_______final Relationship attempts per relationship (final)'   , 'Final relationship'),
        (df_actor[df_actor['ego']],                               'num_actors',             'Ego attempts per number of actors'                                , 'Number of actors'),
    ]

    for df, groupby, title, xlabel in plot_types:
        create_bar_chart(df=df, groupby=groupby, title=title, xlabel=xlabel, width=8, height=4, output_path=output_path)
    
    # iterate through man_id values in df_coords
    for man_id in df_coordinates['man_id'].unique():
        create_coordinates_chart(df=df_coordinates, man_id=man_id, title=f'Coordinates of paths for maneuver {man_id}', 
                                 width=8, height=8, output_path=output_path, fix_scale=True)

if __name__ == "__main__":
    main()
