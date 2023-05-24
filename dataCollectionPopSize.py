import numpy as np
import pandas as pd
import subprocess

data = []
def_num_offspring = 20

pop_size_params = [4]

#j = 0
j = 5

#while j < 10:
while j == 5:
    for pop in pop_size_params:
        
        subprocess.run(["bash runHPTuning.sh " + str(pop) + " " + 
                        str(def_num_offspring) + " " + 
                        'examples/basic/4actors/' + str(j) + '-0/d-nsga.scenic',
                        ""], shell=True)
        df = pd.read_json('examples/basic/_output/_measurementstats.json')
        json_path = "data/town02-4-actor-scene-" + str(j) + "-0-pop-" + str(pop) + ".json"
        df.to_json(f"{json_path}")
        df = df['results'].apply(pd.Series)
        dff = df['solutions'].apply(pd.Series)
        dff = dff['sol-0'].apply(pd.Series)

        i = 0
        while (i < 10):
            print('started loop')
            data.append([4, str(j) + '-0', pop, def_num_offspring, df['time'].values[i], dff['CON_sat_%'].values[i]])
            i += 1
            
        subprocess.run(["bash runHPTuning.sh " + str(pop) + " " +
                        str(def_num_offspring) + " " +
                        'examples/basic/2actors/' + str(j) + '-0/d-nsga.scenic',
                        ""], shell=True)
        
        df = pd.read_json('examples/basic/_output/_measurementstats.json')
        json_path = "data/town02-2-actor-scene-" + str(j) + "-0-pop-" + str(pop) + ".json"
        df.to_json(f"{json_path}")
        df = df['results'].apply(pd.Series)
        dff = df['solutions'].apply(pd.Series)
        dff = dff['sol-0'].apply(pd.Series)
        
        i = 0
        while (i < 10):
            print('started loop')
            data.append([2, str(j) + '-0', pop, def_num_offspring, df['time'].values[i], dff['CON_sat_%'].values[i]])
            i += 1
            
        subprocess.run(["bash runHPTuning.sh " + str(pop) + " " +
                        str(def_num_offspring) + " " +
                        'examples/basic/3actors/' + str(j) + '-0/d-nsga.scenic',
                        ""], shell=True)
        
        df = pd.read_json('examples/basic/_output/_measurementstats.json')
        json_path = "data/town02-3-actor-scene-" + str(j) + "-0-pop-" + str(pop) + ".json"
        df.to_json(f"{json_path}")
        df = df['results'].apply(pd.Series)
        dff = df['solutions'].apply(pd.Series)
        dff = dff['sol-0'].apply(pd.Series)
        
        i = 0
        while (i < 10):
            print('started loop')
            data.append([3, str(j) + '-0', pop, def_num_offspring, df['time'].values[i], dff['CON_sat_%'].values[i]])
            i += 1
            
        if j == 0 and pop == 5:
            df10 = pd.DataFrame(data, columns=['Actors','File Name', 'Population Size', 'Number of Offsprings', 'Time', 'Success'])
            df10.to_excel(r'data/town02-scene-data.xlsx', index=False)
        else:
            df10 = pd.DataFrame(data, columns=['Actors','File Name', 'Population Size', 'Number of Offsprings', 'Time', 'Success'])
            df11 = pd.read_excel('data/town02-scene-data.xlsx')
            df12 = pd.concat([df10, df11])
            df12.to_excel(r'data/town02-scene-data.xlsx', index=False)
            
        data = []

    j += 1
    


    

        
    
