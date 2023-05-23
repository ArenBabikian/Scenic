import shutil

# RQ1
# for m in ['tram05', 'town02', 'zalaFullcrop']:
#     for c in ['2actors', '3actors', '4actors']:
#         for i in range(10):
#             print(f'DOING {m}-{c}-{i}-0')
#             for a in ['d-sc1', 'd-sc2', 'd-sc3']:
#                 src = rf"C:\git\2-results\2-results\RQ1\{m}\{c}\{i}-0\{a}"
#                 tgt = rf"docker\results\RQ2\{m}\{c}\{i}-0\{a}"

#                 shutil.copytree(src, tgt)

# RQ3
for m in ['zalaFullcrop']:
    for c in ['none', 'r', 'rc', 'rcp', 'rcpd', 'rcpdv']:
        for i in range(10):
            print(f'DOING {m}-{c}-{i}-0')
            src = rf"docker\results\RQ3NEW\{m}\cons\{c}\{i}\nsga3-categories"
            tgt = rf"docker\results\RQ3\{m}\cons\{c}\{i}\nsga3-categories"

            shutil.copytree(src, tgt)


# scp -P 18327 -r "cloud@vm.fured.cloud.bme.hu:/home/cloud/arenb/Scenic/dockerScale" docker/results/RQ4