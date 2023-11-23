import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

FILE_FORMAT = 'PDF'
PRVENTABLE_THRESHOLD = 60

style_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

color_blind_friendly = False

# Change colors to color blind friendly colors
if color_blind_friendly:
    plt.style.use('tableau-colorblind10')
    color_indices = [0, 1, 5, 7, 8, 9, 2, 3, 4, 6]
    style_colors = [style_colors[i] for i in color_indices]


def agg_attempt_collision_near_miss(data):
    d = {}
    d['attempts'] = data['num_collisions'].count()
    d['collision'] = data['num_collisions'].sum()
    d['near miss'] = (data['near_miss_occurance'].sum() - d['collision'])
    d['preventative measure'] = (data['num_preventative_maneuvers'] > 0).sum()
    
    d['collision'] = d['collision'] / d['attempts']
    d['near miss'] = d['near miss'] / d['attempts']
    d['preventative measure'] = d['preventative measure'] / d['attempts']
    d['attempts'] = d['attempts'] / d['attempts']
    return pd.Series(d)


def agg_attempt_preventable_collision_near_miss(data):
    d = {}
    d['attempts'] = data['num_collisions'].count()
    d['total collision'] = data['num_collisions'].sum()
    d['vis preventable collision'] = data[(data['prevent_vis_stretch_frames'] >= PRVENTABLE_THRESHOLD)]['num_collisions'].sum()
    d['lid preventable collision'] = data[(data['prevent_lid_stretch_frames'] >= PRVENTABLE_THRESHOLD)]['num_collisions'].sum()
    d['both preventable collision'] = data[(data['prevent_both_stretch_frames'] >= PRVENTABLE_THRESHOLD)]['num_collisions'].sum()
    # d['either preventable collision'] = d['vis preventable collision'] + d['lid preventable collision'] - d['both preventable collision']
    d['preventable collision'] = data[(data['prevent_vis_stretch_frames'] >= PRVENTABLE_THRESHOLD) | (data['prevent_lid_stretch_frames'] >= PRVENTABLE_THRESHOLD)]['num_collisions'].sum()
    # d['preventable collision'] = data[(data['prevent_vis_stretch_frames'] >= 30) | (data['prevent_lid_stretch_frames'] >= 30)]['num_collisions'].sum()
    d['non-preventable collision'] = d['total collision'] - d['preventable collision']

    d['near miss'] = (data['near_miss_occurance'].sum() - d['total collision'])
    d['no incident'] = d['attempts'] - d['total collision'] - d['near miss']
    d['preventative measure'] = (data['num_preventative_maneuvers'] > 0).sum()
    
    d['total collision'] = d['total collision'] / d['attempts']
    d['vis preventable collision'] = d['vis preventable collision'] / d['attempts']
    d['lid preventable collision'] = d['lid preventable collision'] / d['attempts']
    d['both preventable collision'] = d['both preventable collision'] / d['attempts']
    # d['either preventable collision'] = d['either preventable collision'] / d['attempts']
    d['preventable collision'] = d['preventable collision'] / d['attempts']
    d['non-preventable collision'] = d['non-preventable collision'] / d['attempts']
    d['near miss'] = d['near miss'] / d['attempts']
    d['no incident'] = d['no incident'] / d['attempts']
    d['preventative measure'] = d['preventative measure'] / d['attempts']
    d['attempts'] = d['attempts'] / d['attempts']
    return pd.Series(d)


def create_bar_chart(df, groupby, title, xlabel, width, height, output_path, rotate_ticks=False):
    # df_agg = df.groupby([groupby]).apply(agg_attempt_collision_near_miss)
    df_agg = df.groupby([groupby]).apply(agg_attempt_preventable_collision_near_miss)
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(width, height))
    # Extracting data for plotting
    categories = df_agg.index
    attributes = ['preventable collision', 'non-preventable collision', 'near miss', 'preventative measure', 'no incident']
    # attributes = ['attempts', 'collision']
    # data = df_agg[attributes].values

    # # Set the bar width
    bar_width = 0.4

    # df_agg[['attempts']].plot.bar(width = 0.2, position = -1, stacked = True, ax = ax, color = 'tab:blue')
    df_agg[['preventable collision', 'non-preventable collision', 'near miss', 'no incident']].plot.bar(width = bar_width, position = -0.5, stacked = True, ax = ax, edgecolor='white', color = ['tab:red', 'tab:gray', 'tab:orange', 'tab:olive'])
    # df_agg['near miss'].plot.bar(width = 0.2, position = 1, stacked = True, ax = ax, color = 'orange')
    df_agg[['preventative measure']].plot.bar(width = bar_width, position = -1.5, stacked = True, ax = ax, edgecolor='white', color = 'tab:green')

    # # Create positions for bars
    x = range(len(categories))
    # x_positions = []
    # for i in [0, 1, 1, 2]:
    #     x_positions.append([j + i * bar_width for j in x])

    # # Create the bars
    # for i in range(len(attributes)):
    #     plt.bar(x_positions[i], data[:, i], width=bar_width, label=attributes[i])

    # Set x-axis labels
    # plt.xticks([i + (len(attributes) + 1) / 2 * bar_width for i in x], categories, rotation=90 if rotate_ticks else 0)    # This is for total collision
    plt.xticks([i + 1.5 * bar_width for i in x], categories, rotation=90 if rotate_ticks else 0)    # This is for total collision
    # plt.xticks([i + (len(attributes)) / 2 * bar_width for i in x], categories, rotation=90 if rotate_ticks else 0)        # This is for preventable and non-preventable collision

    # Set the title and legend
    plt.title(title, y=1.2)
    # plt.legend()
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), shadow=False, ncol=5, labels=['Prev. Coll.', 'Non-Prev. Coll.', 'Near-Miss', 'No Incident', 'Prev. Measure'], fontsize=10)

    # Add axis titles
    ax.set_xlabel(xlabel)

    # Show the plot
    plt.tight_layout()

    # Save the plot
    filename = title.replace(' ', '-')
    os.makedirs(f'{output_path}', exist_ok=True)
    plt.savefig(f'{output_path}/{filename}.{FILE_FORMAT}')
    
    os.makedirs(f'{output_path}/csv', exist_ok=True)
    df_agg.to_csv(f'{output_path}/csv/{filename}.csv')

    os.makedirs(f'{output_path}/latex', exist_ok=True)
    with open(f'{output_path}/latex/{filename}.tex', 'w') as f:
        f.write(df_agg.to_latex())

    # plt.show()
    plt.close()


def create_coordinates_chart(df, man_id, title, width, height, output_path, fix_scale=False):
    # Filter the DataFrame based on the condition 'man_id'
    filtered_df = df[(df['man_id'] == man_id) & (df['actor_id'] == 0)]

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(width, height))
    if fix_scale:
        ax.set_aspect('equal', adjustable='box')

    # Define discrete colors for each unique 'num_actors' value
    unique_num_actors = filtered_df['num_actors'].unique()
    # colors = plt.cm.tab10.colors[:len(unique_num_actors)]
    colors = style_colors[:len(unique_num_actors)]

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
    os.makedirs(f'{output_path}/coordinates', exist_ok=True)
    plt.savefig(f'{output_path}/coordinates/{title}.{FILE_FORMAT}')
    plt.close()


def create_box_plot(df_actor, output_path):
    df_actor_with_accident_melted = pd.melt(df_actor[df_actor['num_collisions'] > 0].rename(columns={
                'prevent_vis_tot_frames': 'revent_visual_total_frames',
                # 'prevent_vis_stretch_frames' : 'prevent_visual_stretch_frames',
                'prevent_vis_tail_frames' : 'prevent_visual_tail_frames',
                'prevent_lid_tot_frames' : 'prevent_lidar_total_frames',
                # 'prevent_lid_stretch_frames' : 'prevent_lidar_stretch_frames',
                'prevent_lid_tail_frames' : 'prevent_lidar_tail_frames',
                'prevent_both_tot_frames' : 'prevent_both_total_frames',
                # 'prevent_both_stretch_frames' : 'prevent_both_stretch_frames',
                'prevent_both_tail_frames' : 'prevent_both_tail_frames'
            }, inplace=False),
            value_vars=[
                'revent_visual_total_frames',
                # 'prevent_visual_stretch_frames',
                'prevent_visual_tail_frames',
                'prevent_lidar_total_frames',
                # 'prevent_lidar_stretch_frames',
                'prevent_lidar_tail_frames',
                'prevent_both_total_frames',
                # 'prevent_both_stretch_frames',
                'prevent_both_tail_frames',
                ],
                value_name='# of frames visible',
            )
    df_actor_with_accident_melted['Sensor'] = df_actor_with_accident_melted['variable'].apply(lambda x: x.split('_')[1])
    df_actor_with_accident_melted['Aggregation'] = df_actor_with_accident_melted['variable'].apply(lambda x: x.split('_')[2])

    # Define a custom color palette
    custom_palette = {"visual": style_colors[0], "lidar": style_colors[1], "both": style_colors[2]}

    # Set the style of the plot (optional)
    sns.set(style="whitegrid")

    # Create the box plot using Seaborn
    plt.figure(figsize=(8, 4))  # Set the figure size
    sns.boxplot(data=df_actor_with_accident_melted, x='Aggregation', y='# of frames visible', hue='Sensor', palette=custom_palette)

    # Set the title and labels
    plt.title('Number of frames visible by Aggregation and Sensor')
    plt.xlabel('Aggregation method')
    plt.ylabel('Number of frames visible')

    plt.tight_layout()

    # Save the plot
    plt.savefig(f'{output_path}/frames-visible.{FILE_FORMAT}')

    # Show the plot
    # plt.show()
    plt.close()


def create_closest_points_plot(df_coords, output_path):
    # Filter the dataframes as in your code
    gt_path = df_coords[(df_coords['num_actors'] == 1) & (df_coords['man_id'] == 'road2281_lane0') & (df_coords['scenario_instance_id'] == 7) & (df_coords['rep_id'] == 0)]
    other_path = df_coords[(df_coords['num_actors'] == 3) & (df_coords['man_id'] == 'road2281_lane0') & (df_coords['scenario_instance_id'] == 2) & (df_coords['rep_id'] == 0)]

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define the x-axis range
    min_x = -122
    max_x = -119

    # Filter data for the specified x-axis range
    other_path_zoomed = other_path[(other_path['x'] > min_x) & (other_path['x'] < max_x)]
    gt_path_zoomed = gt_path[(gt_path['x'] > min_x) & (gt_path['x'] < max_x)]

    # Create dictionaries to store closest points and counts
    closest_points = {}
    number_of_closest_points = {}
    number_of_closest_points2 = [0] * len(gt_path_zoomed)

    # Calculate closest points
    for ind in other_path_zoomed.index:
        other_point = other_path_zoomed.loc[ind]
        # other_location = (other_point['x'], other_point['y'])
        distances, gt_indices = zip(*[(np.sqrt((other_point['x'] - gt_point['x'])**2 + (other_point['y'] - gt_point['y'])**2), gt_tr_ind) for gt_tr_ind, gt_point in gt_path_zoomed.iterrows()])
        closest_point_id = np.argmin(distances)
        closest_point_index = gt_indices[closest_point_id]
        closest_points[ind] = closest_point_index
        number_of_closest_points[closest_point_index] = number_of_closest_points.get(closest_point_index, 0) + 1
        number_of_closest_points2[closest_point_id] += 1

    # Plot the ground truth path
    ax.scatter(gt_path_zoomed['x'], gt_path_zoomed['y'], marker='o', label='Ground Truth', c='blue')

    # Plot the other path
    ax.scatter(other_path_zoomed['x'], other_path_zoomed['y'], marker='o', label='Other Path', c='red')

    # Plot lines connecting closest points
    for other_point_ind, gt_point_ind in closest_points.items():
        ax.plot([other_path_zoomed.loc[other_point_ind]['x'], gt_path_zoomed.loc[gt_point_ind]['x']],
                [other_path_zoomed.loc[other_point_ind]['y'], gt_path_zoomed.loc[gt_point_ind]['y']],
                color='black', linewidth=1)

    # Add text with the number of closest points on the ground truth path
    for x, y, text in zip(gt_path_zoomed['x'], gt_path_zoomed['y'], number_of_closest_points2):
        ax.text(x, y, str(text), horizontalalignment='center', verticalalignment='bottom')

    # Set x and y axis limits
    ax.set_xlim([-122, -119])
    ax.set_ylim([144.02, 144.065])

    # Add axis labels and legend
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.legend()

    # Set the title
    ax.set_title('Path Coordinates')

    # Save the plot
    plt.savefig(f'{output_path}/closest-points.{FILE_FORMAT}')

    # Show the plot
    # plt.show()
    plt.close()


def create_collision_near_miss_preventative_matrix_table(df, output_path):
    d = {}
    d['attempts_preventative'] = df[df['num_preventative_maneuvers'] > 0]['num_collisions'].count()
    d['attempts_no_preventative'] = df[df['num_preventative_maneuvers'] == 0]['num_collisions'].count()
    d['collision_preventative'] = df[df['num_preventative_maneuvers'] > 0]['num_collisions'].sum()
    d['collision_no_preventative'] = df[df['num_preventative_maneuvers'] == 0]['num_collisions'].sum()
    d['near_miss_preventative'] = (df[df['num_preventative_maneuvers'] > 0]['near_miss_occurance'].sum() - d['collision_preventative'])
    d['near_miss_no_preventative'] = (df[df['num_preventative_maneuvers'] == 0]['near_miss_occurance'].sum() - d['collision_no_preventative'])
    d['nothing_preventative'] = df[(df['num_preventative_maneuvers'] > 0) & (df['near_miss_occurance'] == 0)]['num_collisions'].count()
    d['nothing_no_preventative'] = df[(df['num_preventative_maneuvers'] == 0) & (df['near_miss_occurance'] == 0)]['num_collisions'].count()
    
    d['collision_preventative'] = d['collision_preventative'] / d['attempts_preventative'] * 100
    d['collision_no_preventative'] = d['collision_no_preventative'] / d['attempts_no_preventative'] * 100
    d['near_miss_preventative'] = d['near_miss_preventative'] / d['attempts_preventative'] * 100
    d['near_miss_no_preventative'] = d['near_miss_no_preventative'] / d['attempts_no_preventative'] * 100
    d['nothing_preventative'] = d['nothing_preventative'] / d['attempts_preventative'] * 100
    d['nothing_no_preventative'] = d['nothing_no_preventative'] / d['attempts_no_preventative'] * 100

    df_matrix = pd.DataFrame.from_dict({
        'Preventative measure': [True, False],
        'Collision': [d['collision_preventative'], d['collision_no_preventative']],
        'Near miss': [d['near_miss_preventative'], d['near_miss_no_preventative']],
        'Nothing': [d['nothing_preventative'], d['nothing_no_preventative']]
    })

    os.makedirs(f'{output_path}/latex/', exist_ok=True)
    with open(f'{output_path}/latex/tab-result-per-measure.tex', 'w') as f:
        f.write(df_matrix.to_latex())

    return df_matrix


def main():
    input_path = 'fse/data-sim'
    output_path = 'fse/figures_all_TEST_2'
    os.makedirs(output_path, exist_ok=True)

    map_junction_names = ['Town05_2240', 'Town04_916']
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
    df_actor['num_adv_actors'] = df_actor['num_actors'].astype(int) - 1
    df_relationship = pd.concat(relationship_list)
    df_coordinates = pd.concat(coordinatess_list)
    

    plot_types = [
        # (df_actor[(df_actor['ego']) & (df_actor['maneuver.id'] == 'road962_lane0')], 'scenario_spec_id','ego____specific Ego attempts per maneuver'            , '(road962_lane0) Maneuver instance id'),
        # (df_actor[(df_actor['ego']) & (df_actor['maneuver.id'] == 'road974_lane0')], 'scenario_spec_id','ego____specific Ego attempts per maneuver'            , '(road974_lane0) Maneuver instance id '),
        (df_actor[df_actor['ego']],                               lambda _ : True,          'Total'                        , 'Total', False),
        (df_actor[df_actor['ego']],                               'maneuver.type',          'Attempts per maneuver type'                   , 'Maneuver type', False),
        (df_actor[(df_actor['ego']) & (df_actor['num_actors'] == '2')],  'maneuver.type',     'Attempts per maneuver type (2 actor only)'                   , 'Maneuver type', False),
        (df_actor[df_actor['ego']],                               'num_adv_actors',         'Attempts per number of adversarial actors'    , 'Adversarial actors', False),
        (df_actor[df_actor['ego']],                               'maneuver.start_lane_id', 'Attempts per start lane'                      , 'Start lane', True),
        (df_actor[df_actor['ego']],                               'maneuver.end_lane_id',   'Attempts per end lane'                        , 'End lane', True),
        (df_actor[~df_actor['ego']],                              'maneuver.id',            'Non-ego attempts per maneuver'                        , 'Maneuver id', True),
        (df_actor[~df_actor['ego']],                              'maneuver.type',          'Non-ego attempts per maneuver type'                   , 'Maneuver type', False),
        (df_actor[~df_actor['ego']],                              'maneuver.start_lane_id', 'Non-ego attempts per start lane'                      , 'Start lane', True),
        (df_actor[~df_actor['ego']],                              'maneuver.end_lane_id',   'Non-ego attempts per end lane'                        , 'End lane', True),
        (df_relationship[df_relationship['time'] == 'initial'],   'relationship',           'Relationship attempts per relationship (initial)' , 'Initial relationship', False),
        (df_relationship[df_relationship['time'] == 'final'],     'relationship',           'Relationship attempts per relationship (final)'   , 'Final relationship', False),
        (df_actor[df_actor['ego']],                               'num_actors',             'Ego attempts per number of actors'                                , 'Number of actors', False),
    ]

    for df, groupby, title, xlabel, rotate_ticks in plot_types:
        create_bar_chart(df=df, groupby=groupby, title=title, xlabel=xlabel, width=8, height=4, output_path=output_path, rotate_ticks=rotate_ticks)
    
    # iterate through man_id values in df_coords
    for man_id in df_coordinates['man_id'].unique():
        create_coordinates_chart(df=df_coordinates, man_id=man_id, title=f'Coordinates of paths for maneuver {man_id}', 
                                 width=8, height=8, output_path=output_path, fix_scale=True)

    create_box_plot(df_actor, output_path)
    create_closest_points_plot(df_coordinates, output_path)

    # for "tab:result-per-measure"
    create_collision_near_miss_preventative_matrix_table(df_actor[df_actor['ego']], output_path=output_path)


if __name__ == "__main__":
    main()
