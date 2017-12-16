un preiction model: 
```
python run.py
```
to read test_input.txt and write to test_output.txt.

Warning: it will delete test_input.txt

### Fake News Chanllenge: 
```
http://www.fakenewschallenge.org/
```

- The model is trained based on the fnc-1-baseline
`https://github.com/FakeNewsChallenge/fnc-1-baseline`
Some useful tools and feature_engineering.py are also come from fnv-1-baseline, which are collected in ./baseline/

- The current model 
`gbdt_res_with_w2v.pickle`
is the baseline model added with sentence-wise pooling word2vec features using Google pretrained word2vec
`https://code.google.com/archive/p/word2vec/`
or simply download from
`https://github.com/mmihaltz/word2vec-GoogleNews-vectors`
