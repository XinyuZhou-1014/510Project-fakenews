import collections
import os
import numpy as np

def write_vec_top(top=10000):
    with open('GoogleNews-vectors-negative300.txt', 'r', encoding='utf-8') as f:
        with open("google_vec_top_%s.txt" % top, 'w', encoding='utf-8') as fw:
            i = 0
            error = 0
            f.readline()  # skip the first line, i.e. '3000000 300\n'
            for i in range(top):
                s = f.readline()
                fw.write(s)


def read_helper(s):
    line = s.strip().split()
    try:
        assert len(line) == 301
    except:
        print(s)
        return None, None
    word, vec = line[0], line[1:]
    vec = np.array(list(map(float, vec)))
    return word, vec


def read_vec_top(top=10000, default_vec=None, auto_generate=False):
    if default_vec is None:
        default_vec = [0.0] * 300
    assert len(default_vec) == 300, "default_vec should have dimension of <300>."
    default_vec = np.array(default_vec)
    if auto_generate and (not os.path.exists("google_vec_top_%s.txt" % top)):
        print("No top %s file yet, first generate" % top)
        write_vec_top(top)

    with open("google_vec_top_%s.txt" % top, 'r', encoding='utf-8') as f:
        s = f.readlines()
    

    l = list(map(read_helper, s))
    word2vec = collections.defaultdict(lambda: default_vec)
    d = {w: v for w, v in l}
    word2vec.update(d)

    freq_rank = collections.defaultdict(lambda: top)
    d = {l[i][0]: i for i in range(top)}
    freq_rank.update(d)

    # print("return word2vec and freq_rank as defaultdict")
    return word2vec, freq_rank


if __name__ == '__main__':
    word2vec, freq_rank = read_vec_top(2000, auto_generate=True)
# print(freq_rank)