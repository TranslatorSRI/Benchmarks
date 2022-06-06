from collections import defaultdict

cond2drug = defaultdict(list)


with open('DrugCondition.txt','r') as inf:
    h = inf.readline()
    for line in inf:
        x = line.strip().split('\t')
        if len(x) < 6:
            continue
        if x[3].upper() == 'FALSE':
            continue
        cond = (x[5],x[4])
        cond2drug[cond].append( (x[1],x[0]) )

with open('../Data/ConditionToTopDrugs.txt','w') as outf:
    outf.write('ConditionID\tConditionName\tDrugID\tDrugName\tRank\tCount\n')
    for cid,cname in cond2drug:
        for i,(drugid,drugname) in enumerate(cond2drug[(cid,cname)]):
            outf.write(f'{cid}\t{cname}\t{drugid}\t{drugname}\t{i+1}\t{len(cond2drug[(cid,cname)])}\n')

