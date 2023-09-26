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
    input_path = 'fse/data-sim/Town05_2240'
    json_data_actor = json.load(open(f'{input_path}/data_actor.json', 'rb'))
    df_actor = pd.json_normalize(json_data_actor, record_path=['actors'])

    json_data_relationship = json.load(open(f'{input_path}/data_relationship.json', 'rb'))
    df_relationships = pd.json_normalize(json_data_relationship, record_path=['relationships'])
    output_path = 'fse/figures'

    df_coords = pd.read_csv(f'{input_path}/path_coords.csv')

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
        create_bar_chart(df=df, groupby=groupby, title=title, width=8, height=4, output_path=output_path)
    
    # iterate through man_id values in df_coords
    for man_id in df_coords['man_id'].unique():
        create_coordinates_chart(df=df_coords, man_id=man_id, title=f'Coordinates of paths for maneuver {man_id}', 
                                 width=8, height=8, output_path=output_path, fix_scale=True)

    # Create a 4x2 grid of subplots
    fig, axs = plt.subplots(2, 4, figsize=(16, 16))

    # Choose the order of man_id values for subplots
    man_id_order = ['road2241_lane0', 'road2242_lane0', 'road2282_lane0', 'road2292_lane0', 'road2280_lane0', 'road2281_lane1', 'road2281_lane0', 'road2280_lane1']

    # Create subplots for each man_id
    for i, man_id in enumerate(man_id_order):
        row, col = divmod(i, 4)  # Calculate the row and column for the subplot
        create_coordinates_composite_chart(df=df_coords, man_id=man_id, title=f'{man_id}', ax=axs[row, col], fix_scale=True)

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the plot
    # plt.show()

    # Save the plot
    plt.savefig(f'{output_path}/Coordinates.{FILE_FORMAT}')

if __name__ == "__main__":
    main()
