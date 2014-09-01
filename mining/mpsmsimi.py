import sys
from multiprocessing import Process, Lock, Manager, current_process
from common.utils import normalize, norm_dot_product
import time
from cStringIO import StringIO

rows = {}
cid2rids = {}
group_dict = {}
max_group_id = 0

def get_group_id(gname):
    global group_dict, max_group_id
    if gname in group_dict:
        return group_dict[gname]
    else:
        group_dict[gname] = max_group_id
        max_group_id += 1
        return group_dict[gname]

def read_input(input_filename):
    fin = open(input_filename, 'r')
    rows = {}
    cid2rids = {}

    for no,line in enumerate(fin):
        if no % 10000 == 0:
            print ' %d\r' % no,
            sys.stdout.flush()
        parts = line.strip().split()
        try:
            rid = int(parts[0])
            columns = parts[1:]
            row_vector = {}
            for col in columns:
                subparts = col.split(':')
                if len(subparts) != 2:
                    continue
                cid = int(subparts[0])
                value = float(subparts[1])
                if value <= 0.1:
                    continue
                row_vector[cid] = value
                #cid2rids.setdefault(cid, []).append(rid)
            items = row_vector.items()
            items.sort(key=lambda x:x[1], reverse=True)
            items = items[:10]
            row_vector = dict(items)
            for cid in row_vector:
                cid2rids.setdefault(cid, []).append(rid)
            normalize(row_vector)
            rows[rid] = row_vector
        except ValueError:
            continue
    fin.close()
    return rows, cid2rids

def worker(tasks, foutput, lock, groups):
    global rows, cid2rids
    name = current_process().name
    buf = StringIO()

    for no, rid in enumerate(tasks):
        if no % 100 == 0:
            lock.acquire()
            foutput.write(buf.getvalue())
            foutput.flush()
            buf.truncate(0)
            lock.release()

        cids = rows[rid].keys()
        rrids = set()
        for cid in cids:
            rrids.update(cid2rids[cid])
        rrids.remove(rid)
        # remove rrids from different category
        rgroups = groups.get(rid, set())
        rrid2simi = {}
        small_rrids = set()
        for rrid in rrids:
            if not groups.get(rrid, set()).intersection(rgroups):
                continue
            small_rrids.add(rrid)
        #print >> sys.stderr, 'rrids: %d -> %d' % (len(rrids), len(small_rrids))
        rrids = small_rrids
        for rrid in rrids:
            rrid2simi[rrid] = norm_dot_product(rows[rid], rows[rrid])
        items = rrid2simi.items()
        items.sort(key=lambda x:x[1], reverse=True)
        items = [item for item in items if item[1]>=0.1][:25]
        buf.write('%d %s\n' % (rid, ' '.join(['%d:%.4f' % item for item in items])))
    else:
        if buf.tell() != 0:
            lock.acquire()
            foutput.write(buf.getvalue())
            foutput.flush()
            buf.truncate(0)
            lock.release()

def read_group(fname):
    '''goods id\tgroup id'''
    print 'read group...'
    finput = open(fname)
    groups = {}

    for line in finput:
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        gid = int(parts[0])
        gname = parts[1]
        groupid = get_group_id(gname)
        groups.setdefault(gid, set()).add(groupid) # gid -> group id set
    finput.close()
    print 'groups of %d items' % len(groups)
    return groups

def main():
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print 'Usage: <input> <output> [group]'
        sys.exit(0)

    print 'read input...'
    sys.stdout.flush()
    global rows, cid2rids
    rows, cid2rids = read_input(sys.argv[1])
    if len(sys.argv) == 4:
        groups = read_group(sys.argv[3])
    else:
        groups = {}
    print 'done.'
    sys.stdout.flush()
    foutput = open(sys.argv[2], 'w')

    # start process and apply tasks
    process_num = 8
    processes = []
    lock = Lock()
    for i in range(process_num):
        process_tasks = [rid for rid in rows.keys() if rid % process_num == i]
        print '%d tasks for #%d' % (len(process_tasks), i)
        p = Process(target=worker, name='WORKER-#%d' % i, args=(process_tasks, foutput, lock, groups))
        p.start()
        processes.append(p)

    # wait for all process to finish
    for p in processes:
        p.join()

    foutput.close()

if __name__ == '__main__':
    main()
