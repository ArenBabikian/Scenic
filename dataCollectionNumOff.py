import numpy as np
import pandas as pd
import subprocess

data = []
def_pop_size = 5

num_offspring = [10, 20, 30, 40, 50, 60]

j = 0

while j < 10:
    for numoff in num_offspring:
        
        subprocess.run(["bash runHPTuning.sh " + str(def_pop_size) + " " + 
                        str(numoff) + " " + 
                        'examples/basic/4actors/' + str(j) + '-0/d-nsga.scenic',
                        ""], shell=True)
        df = pd.read_json('examples/basic/_output/_measurementstats.json')
        json_path = "data/town02-4-actor-scene-" + str(j) + "-0-numoff-" + str(numoff) + ".json"
        df.to_json(f"{json_path}")
        df = df['results'].apply(pd.Series)
        dff = df['solutions'].apply(pd.Series)
        dff = dff['sol-0'].apply(pd.Series)

        i = 0
        while (i < 10):
            print('started loop')
            data.append([4, str(j) + '-0', def_pop_size, numoff, df['time'].values[i], dff['CON_sat_%'].values[i]])
            i += 1
            
        subprocess.run(["bash runHPTuning.sh " + str(def_pop_size) + " " +
                        str(numoff) + " " +
                        'examples/basic/2actors/' + str(j) + '-0/d-nsga.scenic',
                        ""], shell=True)
        
        df = pd.read_json('examples/basic/_output/_measurementstats.json')
        json_path = "data/town02-2-actor-scene-" + str(j) + "-0-numoff-" + str(numoff) + ".json"
        df.to_json(f"{json_path}")
        df = df['results'].apply(pd.Series)
        dff = df['solutions'].apply(pd.Series)
        dff = dff['sol-0'].apply(pd.Series)
        
        i = 0
        while (i < 10):
            print('started loop')
            data.append([2, str(j) + '-0', def_pop_size, numoff, df['time'].values[i], dff['CON_sat_%'].values[i]])
            i += 1
            
        subprocess.run(["bash runHPTuning.sh " + str(def_pop_size) + " " +
                        str(numoff) + " " +
                        'examples/basic/3actors/' + str(j) + '-0/d-nsga.scenic',
                        ""], shell=True)
        
        df = pd.read_json('examples/basic/_output/_measurementstats.json')
        json_path = "data/town02-3-actor-scene-" + str(j) + "-0-numoff-" + str(numoff) + ".json"
        df.to_json(f"{json_path}")
        df = df['results'].apply(pd.Series)
        dff = df['solutions'].apply(pd.Series)
        dff = dff['sol-0'].apply(pd.Series)
        
        i = 0
        while (i < 10):
            print('started loop')
            data.append([3, str(j) + '-0', def_pop_size, numoff, df['time'].values[i], dff['CON_sat_%'].values[i]])
            i += 1
            
        if j == 0 and numoff == 5:
            df10 = pd.DataFrame(data, columns=['Actors','File Name', 'Population Size', 'Number of Offsprings', 'Time', 'Success'])
            df10.to_excel(r'data/town02-scene-data-numoff.xlsx', index=False)
        else:
            df10 = pd.DataFrame(data, columns=['Actors','File Name', 'Population Size', 'Number of Offsprings', 'Time', 'Success'])
            df11 = pd.read_excel('data/town02-scene-data-numoff.xlsx')
            df12 = pd.concat([df10, df11])
            df12.to_excel(r'data/town02-scene-data-numoff.xlsx', index=False)
            
        data = []

    j += 1
    


    

        
    
